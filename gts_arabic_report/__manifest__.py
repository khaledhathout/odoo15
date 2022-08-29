# -*- coding: utf-8 -*-

{
    'name': 'Saudi Localization',
    'version': '15.0.0',
    'sequence': 0,
    'author': 'GeoTechno Soft',
    'website': 'https://www.geotechnosoft.com/',
    'depends': [
        'account',
        'stock',
        #'gts_ar_name',
        'sale_stock',
        'sale',
        'crm',
        'purchase',
        #'gts_profit_analysis_report',
        'gts_company_extra_logo',
        #'gts_bluechip_ticket',

    ],
    'description': '''Reports in Saudi Arabia Localization - Invoice, arabic report, arabic invoice report, invoice arabic report,''',
    'data': [
        "views/report_base.xml",
        "views/invoice_report_templates.xml",
        "views/do_report_templates.xml",
        "views/quote_report_templates.xml",
        "views/purchase_report.xml",
        "views/pro_forma_template.xml",
        # "views/bank_views.xml",
        "views/invoice_views.xml",
        # "views/due_payments_reports.xml",
        "views/sale_order.xml",
        "views/res_company.xml",
    ],
    'assets': {
        'web.report_assets_common': [
            'gts_arabic_report/static/src/css/style.css',
        ], },
    'installable': True,
    'images': ['static/description/banner.png'],
    'price': 15,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'application': True,

}
