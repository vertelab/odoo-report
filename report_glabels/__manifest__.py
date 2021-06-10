# -*- coding: utf-8 -*-
{
    'name': "Report Glabels",

    'summary': """
        Report system for glabels in odoo
    """,
    'description': """
        Report system for glabels in odoo
    """,

    'author': "Vertel AB",
    'website': "vertel.se",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'report',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_base'],
    'external_dependencies': {'python': ['csv',], 'bin': ['glabels-3-batch']},

    # always loaded
    'data': [
        'views/report_view.xml',
    ],
    'sequence' : 5
}
