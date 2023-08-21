# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2022-today Botspot Infoware Pvt. Ltd. <www.botspotinfoware.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
{
    'name': "POS Clear Cart",
    'author': 'Botspot Infoware Pvt. Ltd.',
    'category': 'Point of Sale',
    'summary': """Clear the cart using a single button click in POS screen""",
    'website': 'https://www.botspotinfoware.com',
    'company': 'Botspot Infoware Pvt. Ltd.',
    'maintainer': 'Botspot Infoware Pvt. Ltd.',
    'description': """Clear the cart using a single button click in POS screen""",
    'version': '1.0',
    'depends': ['point_of_sale'],
    'data': [],
    'images':  ['static/description/Pos Clear Cart Banner.gif'],
    'assets': {
        'point_of_sale.assets': [
            'bsi_pos_clear_cart/static/src/js/pos_clear_cart.js'
        ],
        'web.assets_qweb': [
            'bsi_pos_clear_cart/static/src/xml/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
