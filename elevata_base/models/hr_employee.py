from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_number = fields.Char(
        string='Employee Number',
        copy=False,
        tracking=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('employee_number'):
                vals['employee_number'] = self.env['ir.sequence'].next_by_code(
                    'elevata.employee.number') or ''
        return super().create(vals_list)
