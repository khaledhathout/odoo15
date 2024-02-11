# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Warehouse Turnover Analysis Report Odoo App',
    'version': '15.0.0.1',
    'category': 'Warehouse',
    'summary': 'Inventory turnover report Inventory turnover analysis report warehouse turnover ratio analysis report opening and closing stock report warehouse turnover analysis report Inventory turnover excel report Inventory turnover xls report stock turnover analysis',
    'description' :"""
        This odoo app helps user to identify warehouse turnover ratio with opening and closing stock. User can also generate excel report, analysis report and view bar and graph view warehouse turnover analysis report.
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 39,
    "currency": 'EUR',
    'depends': ['sale_stock','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/bi_turnover_report_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/uTCjzPkAOAc',
    "images":['static/description/Banner.png'],
    'license': 'OPL-1',
}
