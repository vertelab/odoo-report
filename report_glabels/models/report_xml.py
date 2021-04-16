# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm, Warning, RedirectWarning


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

    report_type = fields.Selection([
            ('qweb-html', 'HTML'),
            ('qweb-pdf', 'PDF'),
            ('qweb-text', 'Text'),
            ('glabels', 'Glabels'),
        ], required=True, default='qweb-pdf',
        help='The type of the report that will be rendered, each one having its own'
            ' rendering method. HTML means the report will be opened directly in your'
            ' browser PDF means the report will be rendered using Wkhtmltopdf and'
            ' downloaded by the user.')
    glabels_template = fields.Binary(string="Glabels template")
    label_count = fields.Integer(string="Count", default=1,help = "One if you want to fill the sheet with new records, the count of labels of the sheet to fill each sheet with one record")
    col_name = fields.Char(string="Column", help = "(Glabels rows) the name of name column for use in gLabels")
    col_value = fields.Char(string="Column", help = "(Glabels rows) the name of value column for use in gLabels")
    
    def render_glabels(self, res_ids, data):
        template = base64.b64decode(self.glabels_template) if self.glabels_template else ''
        temp = tempfile.NamedTemporaryFile(mode='w+b',suffix='.csv')
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        glabels = tempfile.NamedTemporaryFile(mode='w+b',suffix='.glabels')
        glabels.write(template)
        glabels.seek(0)

        labelwriter = None
        for p in self.env.get(self.model).browse(res_ids).read():
            if not labelwriter:
                _logger.warning("f"*99)
                _logger.warning(p.keys())
                labelwriter = csv.DictWriter(temp,p.keys())
                labelwriter.writeheader()
                
            for c in range(self.label_count):
                labelwriter.writerow({k:isinstance(v, str) and v or str(v) for k,v in p.items()})
        temp.seek(0)
        res = os.system("glabels-3-batch -o %s -l -C -i %s %s" % (outfile.name,temp.name,glabels.name))
        
        outfile.seek(0)
        pdf = outfile.read()
        outfile.close()
        temp.close()
        glabels.close()
        return (pdf,'pdf')

    def _render_qweb_pdf(self, res_ids=None, data=None):
        _logger.warning("".join(traceback.format_stack()))
        report_type = self.report_type.lower().replace('-', '_')
        _logger.warning("#"*999)
        _logger.warning("report type: " + report_type)
        _logger.warning(dir(self.env))
        name = self._name
        if report_type == "glabels":
            return self.render_glabels(res_ids, data)
        else:
            return super(IrActionsReport, self)._render_qweb_pdf(self, res_ids=None, data=None)
