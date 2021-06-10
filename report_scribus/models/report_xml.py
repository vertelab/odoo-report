# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm, Warning, RedirectWarning


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

    report_type = fields.Selection(selection_add=[('scribus_sla', 'Scribus SLA'),('scribus_pdf', 'Scribus PDF')]
    )

    scribus_template = fields.Binary(string="Scribus template")
    @api.multi
    def newfilename(self):
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf',delete=False)
        filename = outfile.name
        outfile.close
        return filename
    @api.multi
    def render(self, record, template):
        #_logger.warning(f"record: {record}")
        # http://jinja.pocoo.org/docs/dev/templates/#working-with-manual-escaping
        sla = tempfile.NamedTemporaryFile(mode='w+t',suffix='.sla')
        #_logger.warning(f"id: {record['id']}")
        #_logger.warning(f"render_template: {self.env['mail.template']._render_template(template, self.model, [record['id']])}")
        sla.write(self.env['mail.template']._render_template(template, self.model, [record["id"]])[record['id']].lstrip())
        sla.seek(0)
        return sla
        #return True
    @api.multi
    def render_scribus(self, res_ids, data):
        template = base64.b64decode(self.scribus_template) if self.scribus_template else ''

        merger = PdfFileMerger()
        outfiles = []
        for p in self.env.get(self.model).browse(res_ids).read():
            outfiles.append(self.newfilename())
            sla = self.render(p, template)
            if self.report_type == 'scribus_sla':
                os.unlink(outfiles[-1])
                return (sla.read(),'sla')

            command = "xvfb-run -a scribus-ng -ns -g %s -py %s -pa -o %s" % (sla.name,os.path.join(get_module_path('report_scribus_14'), 'scribus.py'),outfiles[-1])
            _logger.info(command)
            res = os.system(command)
            sla.close()
            if not os.path.exists(outfiles[-1]) or os.stat(outfiles[-1]).st_size == 0:
                _logger.warning("outfile path doesnt exist")
                raise Warning('There are something wrong with the template or scribus installation')
            merger.append(PdfFileReader(open(outfiles[-1], 'rb')))
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        merger.write(outfile.name)
        for filename in outfiles:
            os.unlink(filename)
        outfile.seek(0)
        pdf = outfile.read()
        outfile.close()
        return (pdf,'pdf')
    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        report_type = self.report_type.lower().replace('-', '_')
        name = self._name
        if report_type == "scribus_sla" or report_type == "scribus_pdf":
            return self.render_scribus(res_ids, data)
        else:
            return super(IrActionsReport, self).render_qweb_pdf(res_ids, data)
