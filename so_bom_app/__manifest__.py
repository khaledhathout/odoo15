# -*- coding: utf-8 -*-
{
    'name':"Bom Selection in Sale Order Line App",
    'author':"Edge Technologies",
    'version' :'15.0.1.0',
    'live_test_url':'https://youtu.be/L0AvXWmBIk4',
    "images":["static/description/main_screenshot.png"],
    'summary':'Select bill of material of selected product in sale order line bom selection mrp bom on sale order line manufacturing bom on sale order line bom selection bill of material on sale order line bill of material selection on sale order line select bom on sale',
    'description': """
      Bom in Sale Order Line
    """,
    'depends': ['base','mrp','sale_management','stock','account'],
    "license" : "OPL-1",
    'data': [
    'security/ir.model.access.csv',
    'views/sale_inherit.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price':12,
    'currency': "EUR",
    'category' : 'Manufacturing'

}
