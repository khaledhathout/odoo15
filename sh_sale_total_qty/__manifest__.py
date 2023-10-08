# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Total Items Quantity | Sale Order Total Items Quantity | Invoice Total Items Quantity",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "15.0.1",
    "category": "Extra Tools",
    "summary": "Display Total Items Quantity In Sales Total Items Quantity In Invoice Total Number Quantity In Quotation Total Numbers Quantity Show Total Number of Quantities To Sale Order Total Number of Quantity In Sales Total No of Quantity Odoo",
    "description": """This module helps to help to show the total number of quantity in sale order & invoice. You can quickly find ordered quantity & invoiced quantity. You can print the total number of quantity in the sale report & invoice report.""",
    "depends": ["sale_management",],
    "data": [
        'views/sh_sale_order_inherited.xml',
        'views/sh_account_move_inherited.xml',
        'views/res_config_setting.xml',
        'report/sh_sale_order_report.xml',
        'report/sh_account_move_report.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "price": "20",
    "currency": "EUR"
}
