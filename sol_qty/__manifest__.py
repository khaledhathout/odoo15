# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sale Order Total Quantity',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Sales',
    'maintainer': 'Craftsync Technologies',
    'description': """

        You can find Remaining Qty and total qty of sale order line & delivered Qty and invoic
    """,
    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['sale_management','stock'],
    'data': [
        'views/sale.xml',
    ],
    
    'images': ['static/description/main_screen.png'],
    'price': 3.99,
    'currency': 'EUR',    
    'installable': True,
    'application': True,
    'auto_install': False,
}
