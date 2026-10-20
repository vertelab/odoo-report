{
    'name': 'Elevata Website Backup',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Backup of website pages, menus and images',
    'author': 'Elevata',
    'website': 'https://www.elevata.se',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': [
        'security/ir.model.access.csv',
        'views/website_backup_views.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': False,
}
