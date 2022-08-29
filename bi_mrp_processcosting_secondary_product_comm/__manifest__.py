# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'MRP Process Costing with Secondary Product',
    'version': '15.0.0.2',
    'category': 'Manufacturing',
    'sequence': 15,
    'summary': 'Manufacturing Several Outputs in MRP Secondary Finished goods in MRP Several Outputs in Manufacturing food industry with costing Manufacturing Secondary Product costing in mrp Secondary Products costing Manufacturing process costing with Secondary products',
    'description': """ This odoo app helps user to calculate process costing of manufacturing and its workorder process with define labour cost and overhead cost from work center. also help to change finished product quantity and produce secondary product alongside with finished products in manufacturing order. """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['base', 'bi_mrp_secondary_product_comm', 'bi_odoo_process_costing_manufacturing'],
    'data': ['security/ir.model.access.csv', 'views/mrp_production.xml'],
    'demo': [],
    'css': [],
    "price": 60,
    "currency": 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
    "live_test_url": 'https://youtu.be/lIHvgUC1GdY',
    "images": ["static/description/Banner.png"],
    'license': 'OPL-1',
}
