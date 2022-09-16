# -*- coding: utf-8 -*-

{
    'name': 'Hide & Show Supplier/Vendor in Products',
    "author": "Edge Technologies",
    'version': '15.0.1.0',
    'live_test_url': "https://youtu.be/bzSNTWkzgn0",
    "images":['static/description/main_screenshot.png'],
    'summary': "Hide vendor field of product hide supplier field of product for specific user hide vendor field or product for specific user hide visible vendor field or product hide vendors on product hide vendors from the product easy to hide and show vendor on product",
    'description': """ This app provide a functionality to hide & show supplier in all products by user configuration.
	hide vendor field of product hide supplier field of product for specific user hide vendor field or product for specific user
	hide and visible vendor field or product hide vendors of product hide vendors from the product easy to hide and show vendor on product
	invisible vendor field on product invisible vendor from product invisible vendor on product.
hide details in product
remove vendor details
remove supplier name
hide details from product

    """,
    "license" : "OPL-1",
    'depends': ['base','purchase','product'],
    'data': [
            'security/supplier_invisible_security.xml',
            'views/invisible_supplier.xml',
            ],
    'installable': True,
    'category': 'Purchase',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
