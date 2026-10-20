# -*- coding: utf-8 -*-
"""Backup of website content: pages, menus, views and images -> zip attachment."""
import base64
import io
import json
import logging
import zipfile

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ElevataWebsiteBackup(models.Model):
    _name = 'elevata.website.backup'
    _description = 'Website Backup'
    _order = 'create_date desc'

    name = fields.Char('Name', required=True)
    website_id = fields.Many2one('website', string='Website')
    backup_date = fields.Datetime('Backup Date', default=fields.Datetime.now)
    attachment_id = fields.Many2one('ir.attachment', string='Backup File',
                                    readonly=True)
    file_size = fields.Integer('Size (bytes)', readonly=True)
    page_count = fields.Integer('Page Count', readonly=True)
    view_count = fields.Integer('View Count', readonly=True)
    image_count = fields.Integer('Image Count', readonly=True)
    note = fields.Text('Note')

    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('backup_in_progress'):
            return super().create(vals_list)
        backups = self.browse()
        for vals in vals_list:
            backups |= self._create_backup(
                name=vals.get('name'), note=vals.get('note'),
                website_id=vals.get('website_id'))
        return backups

    def action_run_backup(self):
        """Manual button + scheduled cron entry point."""
        for _rec in self:  # method may be called on empty set from cron
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
        # Keep at most 12 backups (~3 months weekly)
        old = self.search([('id', '!=', backup.id)], order='create_date desc',
                          offset=12)
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

    def _collect(self, site):
        pages = self.env['website.page'].search(
            [('website_id', 'in', [site.id, False])])
        views = self.env['ir.ui.view'].search([
            ('key', '!=', False),
            '|', ('website_id', '=', site.id),
            ('website_id', '=', False),
            ('key', '=like', 'website.%'),
        ])
        menus = self.env['website.menu'].search(
            [('website_id', 'in', [site.id, False])])
        images = self.env['ir.attachment'].search([
            ('public', '=', True),
            ('mimetype', '=like', 'image/%'),
        ])
        return pages, views, menus, images

    def _create_backup(self, name=None, note=None, website_id=None):
        site = self.env['website'].get_current_website()
        pages, views, menus, images = self._collect(site)

        payload = {
            'website': {'id': site.id, 'name': site.name,
                        'domain': site.domain or ''},
            'pages': [{
                'name': p.name, 'url': p.url, 'view_key': p.view_id.key,
                'arch': p.view_id.arch, 'is_published': p.is_published,
                'website_indexed': p.website_indexed,
            } for p in pages],
            'views': [{
                'key': v.key, 'name': v.name, 'arch': v.arch,
                'website_id': v.website_id.id,
            } for v in views],
            'menus': [{
                'name': m.name, 'url': m.url, 'sequence': m.sequence,
                'parent': m.parent_id.name if m.parent_id else False,
                'page_url': m.page_id.url if m.page_id else False,
            } for m in menus],
        }

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('website_content.json',
                        json.dumps(payload, ensure_ascii=False, indent=2))
            for att in images:
                raw = att.raw
                if raw:
                    safe = att.name.replace('/', '_') or ('img_%s' % att.id)
                    zf.writestr('images/%s_%s' % (att.id, safe), raw)
        data = buf.getvalue()

        ts = fields.Datetime.now().strftime('%Y-%m-%d_%H%M')
        attachment = self.env['ir.attachment'].create({
            'name': 'website_backup_%s.zip' % ts,
            'type': 'binary',
            'raw': data,
            'mimetype': 'application/zip',
            'res_model': self._name,
            'public': False,
        })
        rec = self.with_context(backup_in_progress=True).create({
            'name': name or 'Backup %s' % ts,
            'website_id': website_id or site.id,
            'note': note or False,
            'attachment_id': attachment.id,
            'file_size': len(data),
            'page_count': len(pages),
            'view_count': len(views),
            'image_count': len(images),
        })
        _logger.info('Elevata website backup created: %s pages, %s images',
                     len(pages), len(images))
        return rec
