from odoo import models, fields, api, _


class ElevataAccessProfile(models.Model):
    _name = 'elevata.access.profile'
    _description = 'Access Profile'
    _order = 'sequence, name'

    name = fields.Char(string='Profile Name', required=True)
    sequence = fields.Integer(default=10)
    group_ids = fields.Many2many(
        'res.groups',
        'elevata_access_profile_group_rel',
        'profile_id', 'group_id',
        string='Groups / Permissions',
    )
    note = fields.Text(string='Description')
