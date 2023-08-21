{
    'name': 'Update Product Barcode on POS without reload',
    'summary': 'Add new product or update product barcode on backend. '
               'It will be applied for Point of Sale immediately without reload. ',
    'description': """
        Add new product or update product barcode on backend.
        It will be applied for Point of Sale immediately without reload.
    """,
    'author': "Sonny Huynh",
    'category': 'Point of Sale',
    'version': '0.1',
    'depends': ["base", "barcodes", 'product', 'point_of_sale'],
    'data': [],

    'assets': {
        'point_of_sale.assets': [
            'pos_add_product_barcode_no_reload/static/src/js/pos_scan.js',
            'pos_add_product_barcode_no_reload/static/src/js/pos_db.js',
            'pos_add_product_barcode_no_reload/static/src/js/ProductScreen.js',
        ],
    },

    'support': 'huynh.giang.son.gs@gmail.com',
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
}