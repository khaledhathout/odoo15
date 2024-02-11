# -*- coding: utf-8 -*-
{
    'name': "SMT Alrasheed Purchase Custom",
    'version': '15.0.1.0',
    'license': 'OPL-1',
    'author': 'SMT Technology',
    'category': 'Inventory',
    'depends': ['purchase', 'sale_management', 'stock', 'mrp', 'so_lot_selection','report_xlsx', 'smt_mrp_custom'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/purchase_report_wizard_view.xml',
        'wizard/sale_report_wizard_view.xml',
        'report/report_purchaseorder_document_inherited.xml',
        'report/report_saleorder_document_inherited.xml',
        'views/views.xml',
        'views/product_view.xml',
        'views/sale_order_view.xml',
        'views/quant_view.xml',
        'report/purchase_template.xml',
        'report/sale_template.xml',
        'report/report_action.xml',
    ],

}
