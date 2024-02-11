# -*- coding: utf-8 -*-
{
    'name': "Hierarchy Account Structure HH",

    'summary': """""",

    'description': """
    """,
    'category': 'Accounting/Accounting',
    'version': '1.0',
    'depends': ['account'],
    'data': [
        'data/data_account_type.xml',
        'views/account_account_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smt_hierarchy_account/static/src/scss/account_searchpanel.scss',
        ],
    },
}
