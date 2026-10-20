from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    bankgiro = fields.Char(string="Bankgiro")
