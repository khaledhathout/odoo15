# -*- coding: utf-8 -*-
{
    'name': "MRP Order Backdate ",
    "author": "SMT Technology",
    'version': '15.0.1.0',
    'summary': ' '
               '',
    'description': """
      
    """,
    'depends': ['base','mrp', 'stock', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production.xml',
        'wizard/back_date.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'category': 'stock'

}
