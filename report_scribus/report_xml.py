# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _, registry
from openerp.exceptions import except_orm, Warning, RedirectWarning

from openerp.report import interface
from openerp.modules import get_module_path

import csv
import os
import tempfile
import base64
import PyPDF2

import logging
_logger = logging.getLogger(__name__)


class report_xml(models.Model):
    _inherit = 'ir.actions.report.xml'

    ### Fields
    report_type = fields.Selection(selection_add=[('scribus_sla', 'Scribus SLA'),('scribus_pdf', 'Scribus PDF')])
    scribus_template = fields.Binary(string="Scribus template")

    @api.cr
    def _lookup_report(self, cr, name):
        if 'report.' + name in interface.report_int._reports:
            new_report = interface.report_int._reports['report.' + name]
        else:
            cr.execute("SELECT id, report_type,  \
                        model, glabels_template  \
                        FROM ir_act_report_xml \
                        WHERE report_name=%s", (name,))
            record = cr.dictfetchone()
            if record['report_type'] == 'scribus_sla':
                template = base64.b64decode(record['scribus_template']) if record['scribus_template'] else ''
                new_report = glabels_report(cr, 'report.%s'%name, record['model'],template=template)
            else:
                new_report = super(report_xml, self)._lookup_report(cr, name)
        return new_report
        
        
class scribus_report(object):

    def __init__(self, cr, name, model, template=None ):
        _logger.info("registering %s (%s)" % (name, model))
        self.active_prints = {}

        pool = registry(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        name = name.startswith('report.') and name[7:] or name
        self.template = template
        self.model = model
        try:
            report_xml_ids = ir_obj.search(cr, 1, [('report_name', '=', name)])
            if report_xml_ids:
                report_xml = ir_obj.browse(cr, 1, report_xml_ids[0])
            else:
                report_xml = False            
        except Exception, e:
            _logger.error("Error while registering report '%s' (%s)", name, model, exc_info=True)


    def create(self, cr, uid, ids, data, context=None):
        pool = registry(cr.dbname)
        merger = PyPDF2.PdfFileMerger()
        for p in pool.get(self.model).read(cr,uid,ids):
            outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
            sla = tempfile.NamedTemporaryFile(mode='w+t',suffix='.sla')
            sla.write(self.env['email.template'].render_template(self.template, self.model, p.id).lstrip().encode('utf-8'))
            sla.seek(0)
            res = os.system("xvfb-run -a scribus-ng -ns -g  -py %s -pa -o %s -pa -t %s" % (os.path.join(get_module_path('report_scribus'), 'scribus.py'),outfile.name,sla.name))
            output.seek(0)
            merger.append(output)
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        merger.write(outfile.name)
        outfile.seek(0)
        pdf = outfile.read()
        outfile.close()
        sla.close()
        return (pdf,'pdf')
