import json
from odoo import http
from odoo.http import request


class GoogleMapController(http.Controller):

    @http.route('/elevata_googlemap/_get_googlemap_api_key', type='json', auth='public', website=True)
    def _get_googlemap_api_key(self):
        key = request.env['ir.config_parameter'].sudo().get_param('elevata_googlemap.api_key')
        return json.dumps({
            'googlemap_api_key': key
        })
