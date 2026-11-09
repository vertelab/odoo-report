{
    'name': 'Elevata Google Map Work Order View',
    'version': '18.0.1.0.1',
    'author': 'Elevata',
    'website': 'https://www.elevata.se',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': 'Google Maps view for FSM work orders',
    'depends': [
        'elevata_googlemap',
        'elevata_fsm_flow',
        'contacts',
        'elevata_order_types',
    ],
    'data': [
        'views/fieldservice_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'elevata_googlemap_arbetsorder/static/src/js/order_map_view.js',
            'elevata_googlemap_arbetsorder/static/src/js/order_map_controller.js',
            'elevata_googlemap_arbetsorder/static/src/js/order_map_model.js',
            'elevata_googlemap_arbetsorder/static/src/js/order_map_renderer.js',
            'elevata_googlemap_arbetsorder/static/src/xml/order_map_templates.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
