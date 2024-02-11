{
    'name': "ALrasheed Custom Report",
    'summary': "ALrasheed Custom Report",
    'author': 'Ahmed Abdu',
    'website': 'http://www.smt.sa',
    'category': 'General',
    'version': '15.0.1.0.0',
    'depends': ['base', 'account', 'l10n_sa_invoice', 'purchase', 'sale_management','stock','product','sale_stock','smt_alrasheed_stock_custom'],
    'data': [
        'views/stock_piking_view.xml',
        'reports/report_delivery_note.xml',
        'reports/vat_invoice_template.xml',
        'reports/report_action.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
