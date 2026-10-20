{
    'name': 'Elevata Business Data Backup',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Scheduled JSON/ZIP backup of business data (orders, elevators, contracts, invoices, partners, employees)',
    'author': 'Elevata',
    'website': 'https://www.elevata.se',
    'license': 'LGPL-3',
    'depends': ['mail', 'maintenance', 'fieldservice_vrtl'],
    'data': [
        'security/ir.model.access.csv',
        'views/data_backup_views.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': False,
}
