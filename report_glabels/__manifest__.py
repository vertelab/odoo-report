# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Report: Glabels',
    'version': '14.0.0.0.1',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Add features to gLabel.',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'description': """
    Add fields to gLabel. Add template, count, column name and column value.
    """,
    #'sequence': '1'
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-report/report_glabels',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-report',
    # any module necessary for this one to work correctly
    'depends': ['base', 'report_base'],
    'external_dependencies': {'python': ['csv',], 'bin': ['glabels-3-batch']},

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_view.xml',
        #"wizard/report_test.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo_report.xml',
    ],
    'sequence' : 5
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
