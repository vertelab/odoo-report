from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gotenberg_enabled = fields.Boolean(
        string='Aktivera Gotenberg PDF',
        config_parameter='elevata_gotenberg.enabled',
        default=True,
    )
    gotenberg_url = fields.Char(
        string='Gotenberg URL',
        config_parameter='elevata_gotenberg.url',
        default='http://gotenberg:3000',
    )
    gotenberg_timeout = fields.Integer(
        string='Timeout (sekunder)',
        config_parameter='elevata_gotenberg.timeout',
        default=60,
    )
