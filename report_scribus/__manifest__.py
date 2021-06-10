# -*- coding: utf-8 -*-
{
    'name': 'Scribus Reports',
    'version': '1.3',
    'category': 'Reporting',
    'summary': 'Reports for Scribus publishing system',
    'description': """
        Extention of report using Scribus (http://scribus.net/).
        Scribus is a page layout program for GNU/Linux (also Windows and
        Mac OSX and others). The program supports professional publishing
        features, such as CMYK colors, spot colors, ICC color management
        and versatile PDF creation. Scribus produce output for professional
        printing.

        The link between Odoo and Scribus are sla-documents used as
        templates with a notation (e-mail-template-notation),
        eg ${object.name}.

        sudo add-apt-repository ppa:scribus/ppa
        sudo apt update
        sudo apt install scribus-ng xvfb
        sudo pip install pypdf2
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Reporting',
    'version': '14.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'report_base'],
    'external_dependencies': {'python': ['PyPDF2',], 'bin': ['scribus-ng','xvfb-run']},

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_view.xml',
        #"wizard/report_test.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo_report.xml',
    ],
    'sequence' : 5
}
