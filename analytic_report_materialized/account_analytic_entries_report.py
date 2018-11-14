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
from openerp import tools

import logging
_logger = logging.getLogger(__name__)

class analytic_entries_report(models.Model):
    _inherit = "analytic.entries.report"
    
    id = fields.Integer(index=True)
    date = fields.Date(index=True)
    
    def _select(self):
        select_str = """
                SELECT
                    min(a.id) as id,
                    count(distinct a.id) as nbr,
                    a.date as date,
                    a.user_id as user_id,
                    a.name as name,
                    analytic.partner_id as partner_id,
                    a.company_id as company_id,
                    a.currency_id as currency_id,
                    a.account_id as account_id,
                    a.general_account_id as general_account_id,
                    a.journal_id as journal_id,
                    a.move_id as move_id,
                    a.product_id as product_id,
                    a.product_uom_id as product_uom_id,
                    sum(a.amount) as amount,
                    sum(a.unit_amount) as unit_amount"""
        return select_str

    def _from(self):
        from_str = """
                    account_analytic_line a, account_analytic_account analytic"""
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    a.date, a.user_id,a.name,analytic.partner_id,a.company_id,a.currency_id,
                    a.account_id,a.general_account_id,a.journal_id,
                    a.move_id,a.product_id,a.product_uom_id"""
        return group_by_str

    def _where(self):
        where_str = """
                WHERE
                    analytic.id = a.account_id"""
        return where_str

    @api.model
    def update_materialized_view(self):
        self.env.cr.execute("REFRESH MATERIALIZED VIEW %s" % self._table)

    def init(self, cr):
        cr.execute("select * from INFORMATION_SCHEMA.views where table_name = '%s'" %self._table)
        if cr.dictfetchall():
            tools.drop_view_if_exists(cr, self._table)
        cr.execute("SELECT relname FROM pg_class WHERE relkind='m' AND relname = '%s'" %self._table)
        if cr.dictfetchall():
            cr.execute("DROP MATERIALIZED VIEW IF EXISTS %s CASCADE" % (self._table,))
        cr.execute("""CREATE MATERIALIZED VIEW %s AS (
            %s
                FROM %s%s%s
            )""" % (self._table, self._select(), self._from(), self._where(), self._group_by()))
        for col_name, field in self._columns.iteritems():
            # Old syntax from openerp.osv for some reason
            if field.select:
                indexname = '%s_%s_index' % (self._table, col_name)
                cr.execute("SELECT indexname FROM pg_indexes WHERE indexname = %s and tablename = %s", (indexname, self._table))
                if not cr.dictfetchall():
                    cr.execute("CREATE INDEX %s on %s (%s)" % (indexname, self._table, col_name))

    # ~ def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
    
    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        _logger.warn('\n\ndomain: %s\nfields: %s\ngroupby: %s\noffset: %s\nlimit: %s\norderby: %s\nlazy: %s' % (domain, fields, groupby, offset, limit, orderby, lazy))
        return super(analytic_entries_report, self).read_group(self, cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby, lazy=lazy)
