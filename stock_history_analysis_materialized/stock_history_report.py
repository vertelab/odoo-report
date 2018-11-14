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

class stock_history(models.Model):
    _inherit = 'stock_history.report'

    id = fields.Integer(index=True)
    product_id = fields.Many2one(index=True)
    product_categ_id = fields.Many2one(index=True)

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
        cr.execute("""
            CREATE MATERIALIZED VIEW %s AS (
              SELECT MIN(id) as id,
                date,
                move_id,
                location_id,
                quant_location_id,
                company_id,
                product_id,
                product_categ_id,
                SUM(quantity) as quantity,
                count(*) as nbr_lines,
                COALESCE(SUM(price_unit_on_quant * quantity) / NULLIF(SUM(quantity), 0), 0) as price_unit_on_quant,
                sum(standard_price * quantity) as cost_price,
                sum(price_unit_on_quant * quantity) as product_inventory_value,

                source
                FROM
                ((SELECT
                    stock_move.id AS id,
                    stock_move.id AS move_id,
                    dest_location.id AS location_id,
                    quant_location.id AS quant_location_id,
                    dest_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.categ_id AS product_categ_id,
                    quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    product_product.standard_price as standard_price,
                    stock_move.origin AS source
                FROM
                    stock_move
                JOIN
                    stock_quant_move_rel on stock_quant_move_rel.move_id = stock_move.id
                JOIN
                    stock_quant as quant on stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    stock_location quant_location ON quant.location_id = quant_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state = 'done' AND dest_location.usage in ('internal', 'transit')
                  AND (
                    not (source_location.company_id is null and dest_location.company_id is null) or
                    source_location.company_id != dest_location.company_id or
                    source_location.usage not in ('internal', 'transit'))
                ) UNION ALL
                (SELECT
                    (-1) * stock_move.id AS id,
                    stock_move.id AS move_id,
                    source_location.id AS location_id,
                    quant_location.id AS quant_location_id,
                    source_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.categ_id AS product_categ_id,
                    - quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    product_product.standard_price as standard_price,
                    stock_move.origin AS source
                FROM
                    stock_move
                JOIN
                    stock_quant_move_rel on stock_quant_move_rel.move_id = stock_move.id
                JOIN
                    stock_quant as quant on stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    stock_location quant_location ON quant.location_id = quant_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state = 'done' AND source_location.usage in ('internal', 'transit')
                 AND (
                    not (dest_location.company_id is null and source_location.company_id is null) or
                    dest_location.company_id != source_location.company_id or
                    dest_location.usage not in ('internal', 'transit'))
                ))
                AS foo
                GROUP BY move_id, location_id, quant_location_id, company_id, product_id, product_categ_id, date, price_unit_on_quant, source
            )""" % self._table)
        for col_name, field in self._columns.iteritems():
            # Old syntax from openerp.osv for some reason
            if field.select:
                indexname = '%s_%s_index' % (self._table, col_name)
                cr.execute("SELECT indexname FROM pg_indexes WHERE indexname = %s and tablename = %s", (indexname, self._table))
                if not cr.dictfetchall():
                    cr.execute("CREATE INDEX %s on %s (%s)" % (indexname, self._table, col_name))
