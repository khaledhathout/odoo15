# -*- coding: utf-8 -*-
{
    'name': 'Sales lot Selection SMT',
    'version': '15.0.0',
    "author": "SMT Technology",
    'description': """ 
        Sales order lot selection with available product quantity and restrict non stockable product
    """,
    "summary": 'Sale order lot selection sale stock available lot on sale',
    'depends': ['base', 'stock', 'sale_management'],
    'data': ['views/sale_order_view.xml'],
    'installable': True,
    'auto_install': False,
    'category': 'Sales',

}
