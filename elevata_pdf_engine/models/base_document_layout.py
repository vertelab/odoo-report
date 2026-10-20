from odoo import fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    bankgiro = fields.Char(
        string="Bankgiro",
        related='company_id.bankgiro',
        readonly=False,
    )
