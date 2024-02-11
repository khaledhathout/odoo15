# Copyright 2021 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009

{
    'name': "Account Statement Report",
    'version': '15.0.1.0',
    'license': 'OPL-1',
    'author': 'WeDo Technology',
    'support': 'odoo.support@wedotech-s.com',
    'category': 'account',
    'sequence': 1,
    'depends': ['account', 'account_accountant'],
    'summary': """
       Account Statement Report
       """,

    'data': [
        'security/ir.model.access.csv',
        'wizard/account_statement_report.xml',
        'reports/account_statement_report.xml',

    ],
    'qweb': [

    ],

    'application': False,
}
