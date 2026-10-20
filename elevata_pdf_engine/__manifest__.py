{
    'name': 'Elevata PDF Engine',
    'version': '18.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Elevata document layout, PDF branding and bankgiro field',
    'description': 'Provides the Elevata document layout for all reports, '
                   'including header/footer, background image support, '
                   'and a bankgiro field on res.company.',
    'author': 'Elevata',
    'website': 'https://www.elevata.se',
    'depends': [
        'web',
        'account',
        'sale',
    ],
    'data': [
        'views/report_templates.xml',
        'views/res_company_views.xml',
        'views/document_layout_views.xml',
        'data/report_layout_data.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            'elevata_pdf_engine/static/src/scss/layout_elevata.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
