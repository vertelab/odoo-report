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
from openerp.exceptions import Warning, MissingError
#from openerp.exceptions import except_orm, Warning, MissingError,RedirectWarning

from openerp.report import interface
from openerp.modules import get_module_path

import csv
import os
import tempfile
import base64

import logging
_logger = logging.getLogger(__name__)

class report_xml(models.Model):
    _inherit = 'ir.actions.report.xml'

    ### Fields
    report_type = fields.Selection(selection_add=[('template_render', 'Template Render'),])
    template2render = fields.Binary(string="Template to render")
    @api.one
    @api.depends('report_type','report_name','name')
    def _template2render_name(self):
        self.template2render_name = self.report_name.replace(' ', '_').replace('.sla', '').lower() + '.sla'
    template2render_name = fields.Char(string="Template to render name", compute='_template2render_name')

    @api.cr
    def _lookup_report(self, cr, name):
        if 'report.' + name in interface.report_int._reports:
            new_report = interface.report_int._reports['report.' + name]
        else:
            cr.execute("SELECT id, report_type,  \
                        model, template2render  \
                        FROM ir_act_report_xml \
                        WHERE report_name=%s", (name,))
            record = cr.dictfetchone()
            if record['report_type'] in ['template_render']:
                template = base64.b64decode(record['template2render']) if record['template2render'] else ''
                new_report = scribus_report(cr, 'report.%s'%name, record['model'],template=template,report_type = record['report_type'])
            else:
                new_report = super(report_xml, self)._lookup_report(cr, name)
        return new_report


class template_render_report(object):

    def __init__(self, cr, name, model, template=None,report_type=None ):
        _logger.info("registering %s (%s)" % (name, model))
        self.active_prints = {}

        pool = registry(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        name = name.startswith('report.') and name[7:] or name
        self.template = template
        self.model = model
        self.report_type = report_type
        try:
            report_xml_ids = ir_obj.search(cr, 1, [('report_name', '=', name)])
            if report_xml_ids:
                report_xml = ir_obj.browse(cr, 1, report_xml_ids[0])
            else:
                report_xml = False
        except Exception, e:
            _logger.error("Error while registering report '%s' (%s)", name, model, exc_info=True)


    def render(self, cr, uid, record, template):
        # http://jinja.pocoo.org/docs/dev/templates/#working-with-manual-escaping
        pool = registry(cr.dbname)
        xml = tempfile.NamedTemporaryFile(mode='w+t',suffix='.xml')
        xml.write(pool.get('mail.template').render_template(cr,uid,template, self.model, record['id']).lstrip().encode('utf-8'))
        xml.seek(0)
        return xml

    def create(self, cr, uid, ids, data, context=None):
        pool = registry(cr.dbname)
        for p in pool.get(self.model).read(cr,uid,ids):
            xml = self.render(cr,uid,p,data['template'] or self.template)
            document = xml.read()
            xml.close()
            return (document,'xml')