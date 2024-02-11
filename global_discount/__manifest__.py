# -*- coding: utf-8 -*-
{
    'name': "Global Discount purchase and sales",

    'summary': """
        Global Discount v16.0""",

    'description': """
        - Apply a field in Sales, Purchase and Invoice module to calculate discount after the order lines are inserted.
        - Discount values can be given in two types:
           
           - In Percent
           - In Amount
    """,
    'category': 'Sales Management',
    'version': '1.2.1',
    'license': 'LGPL-3',
    'currency': 'EUR',
    'depends': ['base', 'sale', 'purchase', 'sale_management'],
    'assets': {
        'web.assets_frontend': ['global_discount/static/css/ks_stylesheet.css'],
        'web.assets_backend': [
            '/global_discount/static/js/global_discount.js',
        ],   

    },

    'data': [
        'views/sale_order.xml',
        'views/account_invoice.xml',
        'views/product_template_view.xml',
        'views/purchase_order.xml',
        'views/res_config.xml'
    ],

}
