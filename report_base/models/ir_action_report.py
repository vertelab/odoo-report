fromodoo.exceptions import except_orm, Warning, RedirectWarning

from odoo import models, fields, api, http, registry
import unicodecsv as csv
import os
import tempfile
import base64
import traceback

import logging
_logger = logging.getLogger(__name__)

class IrActionsReport(models.Model):
    
    _inherit = 'ir.actions.report'

    fake_report_type = fields.Selection([('qweb-html', 'HTML'),('qweb-pdf', 'PDF'),('qweb-text', 'Text')], string="Report Type", required=True, default='qweb-pdf',
    help='The type of the report that will be rendered, each one having its own'
        ' rendering method. HTML means the report will be opened directly in your'
        ' browser PDF means the report will be rendered using Wkhtmltopdf and'
        ' downloaded by the user.')

    @api.onchange('fake_report_type')
    def fake_selection_field(self):

        if self.fake_report_type == 'qweb-html' or self.fake_report_type == 'qweb-text':
            self.report_type = self.fake_report_type
        else:
            self.report_type = 'qweb-pdf'
