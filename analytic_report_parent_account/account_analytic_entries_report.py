# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2017 Vertel AB (<http://vertel.se>).
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

from openerp import models, fields, api, _

class AnalyticEntriesReport(models.Model):
    _inherit = "analytic.entries.report"

    parent_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Parent Account')

    def _select(self):
        select_str = super(AnalyticEntriesReport, self)._select()
        select_str += """,
                    analytic.parent_id as parent_account_id"""
        return select_str

    def _group_by(self):
        group_by_str = super(AnalyticEntriesReport, self)._group_by()
        group_by_str += """,
                    analytic.parent_id"""
        return group_by_str
