# -*- coding: utf-8 -*-
{
    "name" : "Reset and Cancel Landed Cost in Odoo",
    "author": "Edge Technologies",
    "version" : "15.0.1.0",
    "live_test_url":'https://youtu.be/9cNvFRfr_7E',
    "images":['static/description/main_screenshot.png'],
    'summary': 'App cancel stock landed cost reset stock landed cost reset landed cost stock landed cost cancel warehouse landed cost cancel landed cost reverse done landed cost cancel correct landed cost rectify landed cost revert stock landed cost freight cost cancel.',
    "description": """
                App for reverse/cancel WMS landed costs
                cancel stock landed cost on odoo, reset stock landed cost, reset landed cost on odoo stock landed cost cancel
                landed cost cancel and reset, warehouse landed cost cancel. cancel warehouse landed cost. landed cost reverse
                cancel done landed cost, correct landed cost, ractify landed cost correct done landed cost, ractify done landed cost
                stock landed cost revert stock landed cost odoo freight cost cancel odoo freight cost reverse freight landed cost cancel landed frieght cost in odoo.
                
                """,
    "license" : "OPL-1",
    "depends" : ['stock_landed_costs'],
    "data": [
        'views/stock_landed_cost_views.xml',
        'views/res_currency.xml',
     ],
    "auto_install": False,
    "installable": True,
    "price": 18,
    "currency": 'EUR',
    "category" : "Warehouse",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
