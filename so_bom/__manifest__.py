# -*- coding: utf-8 -*-
{
    'name': "Bom in Sale Order Line ",
    "author": "SMT Technology",
    'version': '15.0.1.0',
    'summary': 'Select bill of material of selected product in sale order line '
               'line manufacturing bom ',
    'description': """
      Bom in Sale Order Line
    """,
    'depends': ['base', 'mrp', 'sale_management', 'stock', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'category': 'Manufacturing'

}
