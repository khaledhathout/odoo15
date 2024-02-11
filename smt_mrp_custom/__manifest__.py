# -*- coding: utf-8 -*-

{
    'name': 'SMT Manufacturing',
    'category': 'Manufacturing/Manufacturing',
    'author': 'SMT',
    'depends': ['bi_odoo_process_costing_manufacturing', 'maintenance', 'hr_timesheet', 'stock_account', 'mrp_account_enterprise', 'report_xlsx'],
    'description': "",
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/production_report_wizard_view.xml',
        'report/production_order_report.xml',
        'report/production_template.xml',
        'report/report_action.xml',
        'data/mrp_data.xml',
        'views/process_costing_view.xml',
        'views/bom_structrue.xml',
    ],
    'application': True,
}
