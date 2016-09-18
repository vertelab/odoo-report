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

special_reports = [
    'printscreen.list'
]

def _reopen(self, res_id, model):
    return {'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': res_id,
            'res_model': self._name,
            'target': 'new',
    }

class report_buttons_add_print_button(osv.osv_memory):
    '''
    Add Print Button
    '''
    _name = 'report_buttons.add_print_button'
    _description = 'Add print button'

    def _check(self, cr, uid, context):
        irval_mod = self.pool.get('ir.values')
        report = self.pool.get(context['active_model']).browse(cr, uid, context['active_id'], context=context)
        if report.report_name in special_reports:
            return 'exception'
        else:
            ids = irval_mod.search(cr, uid, [('value','=',report.type+','+str(report.id))])
            if not ids:
	            return 'add'
            else:
	            return 'exist'

    def do_action(self, cr, uid, ids, context):
        irval_mod = self.pool.get('ir.values')
        this = self.browse(cr, uid, ids[0], context=context)
        report = self.pool.get(context['active_model']).browse(cr, uid, context['active_id'], context=context)
        event_id = irval_mod.set_action(cr, uid, report.report_name, 'client_print_multi', report.model, 'ir.actions.report.xml,%d' % context['active_id'])
        #~ if report.report_wizard:
            #~ report._set_report_wizard(report.id)
        this.write({'state':'done'})
        if not this.open_action:
            return _reopen(self, this.id, this._model)

        irmod_mod = self.pool.get('ir.model.data')
        iract_mod = self.pool.get('ir.actions.act_window')

        mod_id = irmod_mod.search(cr, uid, [('name', '=', 'act_values_form_action')])[0]
        res_id = irmod_mod.read(cr, uid, mod_id, ['res_id'])['res_id']
        act_win = iract_mod.read(cr, uid, res_id, [])
        act_win['domain'] = [('id','=',event_id)]
        act_win['name'] = _('Client Events')
        return act_win
    
    _columns = {
        'open_action':fields.boolean('Open added action'),
        'state':fields.selection([
            ('add','Add'),
            ('exist','Exist'),
            ('exception','Exception'),
            ('done','Done'),
            
        ],'State', select=True, readonly=True),
    }

    _defaults = {
        'state': _check,
        
    }

report_buttons_add_print_button()

