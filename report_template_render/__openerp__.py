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

{
    'name': 'Template Render Reports',
    'version': '1.3',
    'category': 'Reporting',
    'summary': 'Reports using email render engine',
    'description': """
        Extention for special reports using email render engine. This
        report can render for example simple XML or CSV-files.
        
        The module used as templates with a notation (e-mail-template-notation),
        eg ${object.name}.

""",
    'images': ['images/report_scribus.png'],
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['email_template'],
    'data': [
             "report_view.xml",
             "wizard/report_test.xml",
             ],
    'demo': ['demo_report.xml',],
    "license" : "AGPL-3",
    'installable': True,
    'active': False,
    'application': True,
    'auto_install': False,
}
