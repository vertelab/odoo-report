from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccessProfileLoadWizard(models.TransientModel):
    _name = 'elevata.access.profile.wizard'
    _description = 'Load Access Profile'

    user_id = fields.Many2one('res.users', required=True, readonly=True)
    profile_id = fields.Many2one(
        'elevata.access.profile',
        string='Access Profile',
        required=True,
    )
    replace = fields.Boolean(
        string='Replace existing permissions',
        default=True,
        help='If checked, all permissions are replaced. If unchecked, the profile permissions are added.',
    )

    def action_apply(self):
        """Tillämpa profilen på användaren."""
        self.ensure_one()
        if self.replace:
            self.user_id.groups_id = [(6, 0, self.profile_id.group_ids.ids)]
        else:
            self.user_id.groups_id = [(4, g.id) for g in self.profile_id.group_ids]
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class AccessProfileSaveWizard(models.TransientModel):
    _name = 'elevata.access.profile.save.wizard'
    _description = 'Spara rättighetsprofil'

    user_id = fields.Many2one('res.users', required=True, readonly=True)
    name = fields.Char(string='Profile Name', required=True)
    note = fields.Text(string='Description')
    group_ids = fields.Many2many(
        'res.groups',
        'elevata_access_profile_save_wizard_group_rel',
        'wizard_id', 'group_id',
        string='Permissions',
    )

    def action_save(self):
        """Spara nuvarande rättigheter som ny profil."""
        self.ensure_one()
        self.env['elevata.access.profile'].create({
            'name': self.name,
            'note': self.note,
            'group_ids': [(6, 0, self.group_ids.ids)],
        })
        return {'type': 'ir.actions.client', 'tag': 'reload'}
