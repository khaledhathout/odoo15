# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Secondary Products in Manufacturing/MRP Several Outputs",
    "version" : "15.0.0.0",
    "category" : "Manufacturing",
    'summary': 'Manufacturing Several Outputs in MRP Secondary Finished goods in MRP Several Outputs in Manufacturing food industry Manufacturing Secondary Product in mrp Secondary Products costing with mrp process costing with Secondary product in manufacturing byproduct',
    "description": """
    
                change product quantity,
                change manufacture order quantity,
                change work order quantity,
                change odoo workorder quantity,
                change product quantity,
                manufacturing order qunatity,
                update work order quantity,
                update manufacturing order quantity,
                secondary Product,
                produce secondary product,
                manufacture secondary product,
                secondary roduct with finished product

    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 80,
    "currency": 'EUR',
    "depends" : ['base','mrp',],
    "data": ['security/ir.model.access.csv',
            'views/bom_inherit.xml',
            'views/workorder_view.xml'],
    'demo': [],
    'qweb': [],
    "license":'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/832e_jBsh-k',
    "images":["static/description/Banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
