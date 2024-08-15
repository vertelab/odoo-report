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
    glabels_template = fields.Binary(string="Glabels template")
    label_count = fields.Integer(string="Count", default=1,help = "One if you want to fill the sheet with new records, the count of labels of the sheet to fill each sheet with one record")
    col_name = fields.Char(string="Column", help = "(Glabels rows) the name of name column for use in gLabels")
    col_value = fields.Char(string="Column", help = "(Glabels rows) the name of value column for use in gLabels")
    csv_fields = fields.Text(compute="_get_csv_fields")
    

