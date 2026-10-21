{
    'name': 'Elevata Google Map Elevator View',
    'version': '18.0.1.0.0',
    'author': 'Elevata',
    'website': 'https://www.elevata.se',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': 'Google Maps view for elevator equipment',
    'depends': [
        'elevata_googlemap',
        'elevata_fsm_flow',
        'maintenance_elevator',
    ],
    'data': [
        'views/maintenance_equipment_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'elevata_googlemap_hiss/static/src/js/hiss_map_view.js',
            'elevata_googlemap_hiss/static/src/js/hiss_map_controller.js',
            'elevata_googlemap_hiss/static/src/js/hiss_map_model.js',
            'elevata_googlemap_hiss/static/src/js/hiss_map_renderer.js',
            'elevata_googlemap_hiss/static/src/xml/hiss_map_templates.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
