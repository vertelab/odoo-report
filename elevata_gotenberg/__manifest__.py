{
    'name': 'Elevata Gotenberg PDF',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Use Gotenberg instead of wkhtmltopdf for PDF generation',
    'description': """
        Install this module to use Gotenberg as the PDF engine.
        If the module is not installed, wkhtmltopdf is used (Odoo default).

        Configuration under: Settings -> Technical -> Gotenberg PDF
    """,
    'author': 'Elevata',
    'depends': ['base', 'web'],
    'data': [
        'data/ir_config_parameter.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
