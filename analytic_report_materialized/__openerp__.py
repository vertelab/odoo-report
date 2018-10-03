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
    'name': 'Analytic Entries Report - Materialized',
    'version': '1.0',
    'category': 'Reporting',
    'summary': 'Makes the analytic entries report quicker to read, but not rendered on the fly.',
    'description': """
        Changes the analytic entries report from a regular view to a materialized view.
        Also makes it inheritable in the same fashion as other reports.
        Adds the _select, _from, _where, and _group_by functions.
""",
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['account'],
    'data': [
             ],
    "license" : "AGPL-3",
    'installable': True,
    'active': False,
    'application': False,
    'auto_install': False,
}
