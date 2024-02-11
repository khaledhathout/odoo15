{
    'name': 'Electronic invoice KSA - Invoice | Electronic invoice KSA - Invoice, Credit Note, Bill, Refund | Invoice based on TLV Base64 string QR Code | Saudi Electronic Invoice with Base64 TLV QRCode',
    'version': '15.1.1.5',
    'sequence':1,
    'category': 'Accounting',
    'summary': 'Electronic invoice KSA - Invoice | Electronic invoice KSA - Invoice, Credit Note, Bill, Refund | Invoice based on TLV Base64 string QR Code | Saudi Electronic Invoice with Base64 TLV QRCode',
    
    'description': """
     Electronic invoice KSA - Invoice | Electronic invoice KSA - Invoice, Credit Note, Bill, Refund | Invoice based on TLV Base64 string QR Code | Saudi Electronic Invoice with Base64 TLV QRCode
     Using this module you can print Saudi electronic invoice for Invoice VAT.
     According to Saudi Government QR code with Display Saudi Tax details, Supplier Name, Supplier VAT, Customer Name, Customer VAT, Invoice Date, Create Datetime, Total of VAT, Total of Amount.
     """,
    "author" : "odoobridge",
    "email": 'odoobridge@gmail.com',
    "license": 'OPL-1',
    'depends': ['account'],
    #'depends': ['account','l10n_sa_invoice'],

    'data': [
        'report/vat_invoice_report_print.xml',
        'report/vat_report_action_call.xml',
        'report/simpli_vat_invoice_report.xml',
        'views/sale_purchase_invoice_view.xml',
        'report/invoice_default_attach.xml',
    ],
    "price": 20,
    'currency': 'EUR',
    "live_test_url" : "https://youtu.be/K9XG-_2Tw_Q",   
    # Old Live Link
    #"live_test_url" : "https://youtu.be/yS1ReLJcIbk",  
    "images": ['static/description/invoice.gif'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'ob_saudi_vat_invoice/static/src/css/style.css',
        ],
    },    
}




