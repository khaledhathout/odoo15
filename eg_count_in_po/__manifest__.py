{
    'name': 'Item Count In Purchase Order',
    'version': '15.0',
    'category': 'Purchase',
    'summery': 'Total Items Quantity for Purchase Order',
    'author': 'INKERP',
    'website': "https://www.INKERP.com",
    'depends': ['purchase'],
    
    'data': [
        'views/purchase_order_view.xml',
        'report/purchase_order_report.xml',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
