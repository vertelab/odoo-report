from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_load_access_profile(self):
        """Öppna wizard för att ladda en åtkomstprofil."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Load Access Profile'),
            'res_model': 'elevata.access.profile.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_user_id': self.id},
        }

    def action_save_access_profile(self):
        """Öppna wizard för att spara nuvarande rättigheter som profil."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Save as Access Profile'),
            'res_model': 'elevata.access.profile.save.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_user_id': self.id,
                'default_group_ids': [(6, 0, self.groups_id.ids)],
            },
        }
