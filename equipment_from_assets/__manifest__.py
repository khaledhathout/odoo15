# -*- coding: utf-8 -*-
{
    'name': "Equipment From Assets ",
    "author": "SMT Technology",
    'version': '15.0.1.0',
    'summary': ' '
               '',
    'description': """
      
    """,
    'depends': ['base', 'stock','maintenance','account','account_asset'],
    'data': [
        'views/account_asset.xml',
        'views/maintenance_equipment.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'category': 'stock'

}
