from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    complete_contact_address = fields.Char(
        compute='_compute_complete_address',
        store=True,
    )

    @api.model
    def write_latitude_longitude(self, partner_id):
        if not self.env.user.has_group('base.group_user'):
            return False
        lat = self.env.context.get('partner_latitude')
        lng = self.env.context.get('partner_longitude')
        if partner_id and lat and lng:
            partner = self.env['res.partner'].browse(int(partner_id))
            if partner.exists():
                partner.write({
                    'partner_latitude': lat,
                    'partner_longitude': lng,
                })
        return True

    @api.depends('street', 'zip', 'city', 'state_id', 'country_id')
    def _compute_complete_address(self):
        for record in self:
            parts = []
            if record.street:
                parts.append(record.street)
            if record.zip:
                parts.append(record.zip)
            if record.city:
                parts.append(record.city)
            if record.state_id:
                parts.append(record.state_id.name)
            if record.country_id:
                parts.append(record.country_id.name)
            record.complete_contact_address = ', '.join(parts)
