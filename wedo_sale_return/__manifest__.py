# -*- coding: utf-8 -*-
# Copyright 2020 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009
{
    'name': "Sale Return Managment",
    'version': '15.0.1.0',
    'sequence': 1,
    'author': "Wedo Technology",
    'website': "http://wedotech-s.com",
    'support': 'odoo.support@wedotech-s.com',
    'license': 'OPL-1',
    'category': "Sale",
    'summary': """
Manage Sale picking return and invoice refund    
""",
    'description': """
Manage Sale picking return and invoice refund    

    """,
    'depends': ['sale_stock','stock','account','ob_saudi_vat_invoice', 'report_xlsx'],
    'images': ['images/sale.png', 'images/s_return.png', 'images/tree.png'],

    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'data/return_sequense.xml',
        'wizard/sale_return_report_wizard_view.xml',
        'views/res_config_settings_views.xml',
        'views/sale_return_view.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_inherited.xml',
        'views/templates.xml',
        'reports/sale_return_report.xml',
        'reports/sale_return_template.xml',
        'reports/report_action.xml',
    ],
    'test': [

    ],
    'auto_install': False,
    'installable': True,
}
