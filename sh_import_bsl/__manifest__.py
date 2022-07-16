# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Import bank statement lines from CSV File | Import bank statement lines from Excel file",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "license": "OPL-1",
    "summary": "Import Bank Statement Lines From CSV Import Bank Statement Lines From Excel import Bank Statement Lines From XLS import Bank Statement Lines From XLSX import cash statement Import statement lines import cash register import multiple bank statements Odoo",
    "description": """This module is useful to import bank statement lines from CSV/Excel. You can import custom fields from CSV or Excel.""",
    "version": "15.0.1",
    "depends": [
        "sh_message",
        "account",
    ],
    "application": True,
    "data": [
        "security/import_bsl_security.xml",
        "security/ir.model.access.csv",
        "wizard/import_bsl_wizard.xml",
        "views/account_view.xml",

    ],
    'external_dependencies': {
        'python': ['xlrd'],
    },
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/1rs50ITome0",
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": "EUR"
}
