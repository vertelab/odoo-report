{
    'name': 'Elevata Portal PDF',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'PDF.js viewer for portal documents (sale orders, invoices)',
    'author': 'Elevata',
    'website': 'https://www.elevata.se',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'sale_management',
        'account',
        'portal',
        'web',
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'elevata_portal_pdf/static/src/lib/pdf.mjs',
            'elevata_portal_pdf/static/src/lib/pdf.worker.mjs',
            'elevata_portal_pdf/static/src/js/pdf_viewer.js',
        ],
    },
    'installable': True,
    'application': False,
}
