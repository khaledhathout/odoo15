# -*- coding: utf-8 -*-
{
    'name': "Global Language Translator ",

    'description': """
                     Auto translate Odoo data fields from preferred language to another chosen language and create bilingual printed documents. Reliable auto translate will enter the chosen language in available translation tables from preferred language and allow you to edit if necessary.
                    Save time and cost by reducing manual translated text entry.    
                    """,
    'version': '14.0.1.0.0',
    'summary': '',
    'author': "SimplySolved",
    'company': 'SimplySolved',
    'maintainer': 'SimplySolved',
    'website': "https://www.SimplySolved.ae",
    'price': 0,
    'currency': 'USD',
    'category': 'Uncategorized',
    'depends': ['base', 'product'],
    # always loaded
    'data': [
        'views/product_view.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/main_screenshot.gif']

}
