# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
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
    'name': 'Invoice Report - Materialized',
    'version': '1.0',
    'category': 'Reporting',
    'summary': 'Makes the analytic entries report quicker to read, but not rendered on the fly.',
    'description': """
        Changes the invoice entries report from a regular view to a materialized view.
""",
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['account', 'sale', 'sale_crm'],
    'data': [
             ],
    "license" : "AGPL-3",
    'installable': True,
    'active': False,
    'application': False,
    'auto_install': False,
}
