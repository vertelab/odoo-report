# -*- coding: utf-8 -*-
from odoo.exceptions import RedirectWarning, UserError


from odoo import models, fields, api, http, registry
from odoo.modules import get_module_path
import unicodecsv as csv
import os
import tempfile
import base64
import traceback
import logging
_logger = logging.getLogger(__name__)

_logger.warning("loading model")

try:
    from PyPDF2 import PdfFileMerger, PdfFileReader
except:
    _logger.warning('PyPDF2 missing, sudo pip install pypdf2')

# http://jamesmcdonald.id.au/it-tips/using-gnubarcode-to-generate-a-gs1-128-barcode
# https://github.com/zint/zint

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

   # report_type = fields.Selection(selection_add=[('scribus_sla', 'Scribus SLA'),('scribus_pdf', 'Scribus PDF')],
    fake_report_type = fields.Selection(selection_add=[('scribus_sla', 'Scribus SLA'),('scribus_pdf', 'Scribus PDF')],
    ondelete = {'scribus_sla': 'set default', 'scribus_pdf': 'set default'})

    scribus_template = fields.Binary(string="Scribus template")

    def newfilename(self):
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf',delete=True)
        filename = outfile.name
        outfile.close
        return filename

    def render(self, report_id, record, template):
        sla = tempfile.NamedTemporaryFile(mode='w+t',suffix='.sla',delete=True)
        sla.write(self.env['mail.template']._render_template(template, report_id.model, [record["id"]])[record['id']].lstrip())
        sla.seek(0)
        return sla

    def render_scribus(self,report_id,res_ids, data):
        template = base64.b64decode(report_id.scribus_template).decode("utf-8") if report_id.scribus_template else ''
                
        merger = PdfFileMerger()
        outfiles = []

        for p in self.env.get(report_id.model).browse(res_ids).read():
            outfiles.append(self.newfilename())
            sla = self.render(report_id, p, template)
            if report_id.fake_report_type == 'scribus_sla':
                os.unlink(outfiles[-1])
                return (sla.read(),'sla')

            command = "xvfb-run -a scribus -ns -g %s -py %s -pa -o %s" % (sla.name,os.path.join(get_module_path('report_scribus'), 'scribus.py'),outfiles[-1])
            _logger.info(command)
            res = os.system(command)
            sla.close()
            if not os.path.exists(outfiles[-1]) or os.stat(outfiles[-1]).st_size == 0:
                _logger.warning("outfile path doesnt exist")
                raise UserError('There are something wrong with the template or scribus installation')
            merger.append(PdfFileReader(open(outfiles[-1], 'rb')))
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        merger.write(outfile.name)
        for filename in outfiles:
            os.unlink(filename)
        outfile.seek(0)
        pdf = outfile.read()
        outfile.close()
        return (pdf,'pdf')

    def _render_qweb_pdf(self,report_ref, res_ids=None, data=None):
        report_id = self._get_report(report_ref)
        report_type = report_id.fake_report_type.lower().replace('-', '_')
        if report_type == "scribus_sla" or report_type == "scribus_pdf":
            return self.render_scribus(report_id,res_ids, data)
        else:
            return super(IrActionsReport, self)._render_qweb_pdf(report_ref,res_ids, data)

_logger.warning("model loaded")
