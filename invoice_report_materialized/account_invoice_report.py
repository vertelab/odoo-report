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

from openerp import models, fields, api, _
from openerp import tools

import logging
_logger = logging.getLogger(__name__)

class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    @api.model
    def update_materialized_view(self):
        self.env.cr.execute("REFRESH MATERIALIZED VIEW %s" % self._table)

    def init(self, cr):
        drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE MATERIALIZED VIEW %s as (
            WITH currency_rate (currency_id, rate, date_start, date_end) AS (
                SELECT r.currency_id, r.rate, r.name AS date_start,
                    (SELECT name FROM res_currency_rate r2
                     WHERE r2.name > r.name AND
                           r2.currency_id = r.currency_id
                     ORDER BY r2.name ASC
                     LIMIT 1) AS date_end
                FROM res_currency_rate r
            )
            %s
            FROM (
                %s %s %s
            ) AS sub
            JOIN currency_rate cr ON
                (cr.currency_id = sub.currency_id AND
                 cr.date_start <= COALESCE(sub.date, NOW()) AND
                 (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
        )""" % (
                    self._table,
                    self._select(), self._sub_select(), self._from(), self._group_by()))
    
# TODO: Try to monkeywrench this into openerp.tools
def drop_view_if_exists(cr, viewname):
    cr.execute("select * from INFORMATION_SCHEMA.views where table_name = '%s'" % viewname)
    if cr.dictfetchall():
        cr.execute("DROP view IF EXISTS %s CASCADE" % (viewname,))
    cr.execute("SELECT relname FROM pg_class WHERE relkind='m' AND relname = '%s'" % viewname)
    if cr.dictfetchall():
        cr.execute("DROP MATERIALIZED VIEW IF EXISTS %s CASCADE" % (viewname,))
    cr.commit()
