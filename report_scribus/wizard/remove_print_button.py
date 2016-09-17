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

from openerp.tools.translate import _
from openerp.osv import osv, fields

def _reopen(self, res_id, model):
    return {'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': res_id,
            'res_model': self._name,
            'target': 'new',
    }

class glabel_remove_print_button(osv.osv_memory):
    '''
    Remove Print Button
    '''
    _name = 'report_glabel.remove_print_button'
    _description = 'Remove print button'

    def default_get(self, cr, uid, fields_list, context=None):
        values = {}

        report = self.pool.get(context['active_model']).browse(cr, uid, context['active_id'], context=context)
        irval_mod = self.pool.get('ir.values')
        ids = irval_mod.search(cr, uid, [('value','=',report.type+','+str(report.id))])
        if not ids:
            values['state'] = 'no_exist'
        else:
            values['state'] = 'remove'

        return values

    def do_action(self, cr, uid, ids, context):
        this = self.browse(cr, uid, ids[0], context=context)
        report = self.pool.get(context['active_model']).browse(cr, uid, context['active_id'], context=context)
        irval_mod = self.pool.get('ir.values')
        event_id = irval_mod.search(cr, uid, [('value','=','ir.actions.report.xml,%d' % context['active_id'])])[0]
        res = irval_mod.unlink(cr, uid, [event_id])
        this.write({'state':'done'})
        return _reopen(self, this.id, this._model)
    
    _columns = {
        'state':fields.selection([
            ('remove','Remove'),
            ('no_exist','Not Exist'),
            ('done','Done'),
            
        ],'State', select=True, readonly=True),
    }

glabel_remove_print_button()

