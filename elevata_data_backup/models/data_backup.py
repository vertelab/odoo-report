# -*- coding: utf-8 -*-
"""Backup of business data: orders, elevators, contracts, invoices,
partners, employees -> zip with one JSON file per model."""
import base64  # noqa: F401
import io
import json
import logging
import zipfile

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

BACKUP_MODELS = [
    'res.partner',
    'res.users',
    'hr.employee',
    'maintenance.equipment',
    'fieldservice.order',
    'fieldservice.order.type',
    'elevata.service.contract',
    'elevata.service.contract.line',
    'account.move',
    'account.move.line',
    'elevata.offer',
    'elevata.compliance.journal',
    'elevata.compliance.risk',
    'elevata.compliance.action',
    'elevata.compliance.incident',
    'elevata.compliance.document',
    'elevata.compliance.electrical.plan',
    'product.product',
    'ir.attachment',
]


class ElevataDataBackup(models.Model):
    _name = 'elevata.data.backup'
    _description = 'Business Data Backup'
    _order = 'create_date desc'

    name = fields.Char('Name', required=True)
    backup_date = fields.Datetime('Backup Date', default=fields.Datetime.now)
    attachment_id = fields.Many2one('ir.attachment', string='Backup File',
                                    readonly=True)
    file_size = fields.Integer('Size (bytes)', readonly=True)
    record_count = fields.Integer('Record Count', readonly=True)
    model_count = fields.Integer('Model Count', readonly=True)
    note = fields.Text('Note')

    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('backup_in_progress'):
            return super().create(vals_list)
        backups = self.browse()
        for vals in vals_list:
            backups |= self._create_backup(
                name=vals.get('name'), note=vals.get('note'))
        return backups

    def action_run_backup(self):
        for _rec in self:
            pass
        backup = self._create_backup()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': backup.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def cron_create_backup(self):
        backup = self._create_backup()
        old = self.search([('id', '!=', backup.id)],
                          order='create_date desc', offset=12)
        if old:
            old.mapped('attachment_id').unlink()
            old.unlink()
        return backup

    def action_download(self):
        self.ensure_one()
        if not self.attachment_id:
            return {'type': 'ir.actions.act_url_close'}
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % self.attachment_id.id,
            'target': 'self',
        }

    # ------------------------------------------------------------------

    def _export_model(self, model_name):
        if model_name not in self.env:
            return None, 0
        records = self.env[model_name].search([])
        if not records:
            return [], 0
        # Skip binary/image fields — only metadata kept for attachments
        exclude_types = ('binary', 'image')
        field_names = [
            fname for fname, f in records._fields.items()
            if f.type not in exclude_types
        ]
        data = records.read(field_names, load='_classic_write')
        return data, len(data)

    def _create_backup(self, name=None, note=None):
        buf = io.BytesIO()
        total = 0
        models_done = 0
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for model_name in BACKUP_MODELS:
                try:
                    data, count = self._export_model(model_name)
                except Exception as exc:  # noqa: BLE001
                    _logger.warning(
                        'Data backup: could not export %s: %s',
                        model_name, exc)
                    continue
                if data is None:
                    continue
                fname = model_name.replace('.', '_') + '.json'
                zf.writestr(
                    fname,
                    json.dumps(data, ensure_ascii=False, indent=1,
                               default=str))
                total += count
                if count:
                    models_done += 1
        payload = buf.getvalue()

        ts = fields.Datetime.now().strftime('%Y-%m-%d_%H%M')
        attachment = self.env['ir.attachment'].create({
            'name': 'data_backup_%s.zip' % ts,
            'type': 'binary',
            'raw': payload,
            'mimetype': 'application/zip',
            'res_model': self._name,
            'public': False,
        })
        rec = self.with_context(backup_in_progress=True).create({
            'name': name or 'Data backup %s' % ts,
            'note': note or False,
            'attachment_id': attachment.id,
            'file_size': len(payload),
            'record_count': total,
            'model_count': models_done,
        })
        _logger.info(
            'Elevata data backup created: %s records in %s models',
            total, models_done)
        return rec
