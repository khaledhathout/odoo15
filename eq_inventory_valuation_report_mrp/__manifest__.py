# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

{
    'name': "Inventory Valuation Report with Manufacturing",
    'category': 'Stock',
    'version': '15.0.1.0',
    'author': 'Equick ERP',
    'description': """
        This Module allows you to generate Inventory Valuation Report PDF/XLS wise.
    """,
    'summary': """Inventory Report | Valuation Report | Real Time Valuation Report | Real Time Stock Report | Stock Report | Stock card | Manufacturing Report | Odoo Inventory Report | stock card report | stock card valuation report | stock balance""",
    'depends': ['base', 'stock_account','mrp'],
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_inventory_valuation_mrp_view.xml',
        'report/report.xml',
        'report/valuation_report.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
