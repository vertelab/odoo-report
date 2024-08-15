from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError

from odoo import models, fields, api, http, registry
import unicodecsv as csv
import os
import tempfile
import base64
import traceback

import logging
_logger = logging.getLogger(__name__)

# http://jamesmcdonald.id.au/it-tips/using-gnubarcode-to-generate-a-gs1-128-barcode
# https://github.com/zint/zint

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _get_csv_fields(self):
        self.csv_fields = ','.join(sorted(self.env[self.model]._fields.keys()))
    fake_report_type = fields.Selection(selection_add=[
