# -*- coding: utf-8 -*-
{
    'name': "smt_alrasheed_stock_custom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_report_wizard_view.xml',
        'views/views.xml',
        'views/reports.xml',
        'views/templates.xml',
        'report/stock_template.xml',
        'report/delivery_note_template.xml',
        'report/report_action.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
