{
    'name': "Odoo Github Authenticator",
    'summary': """
                Odoo Github Authenticator helps to authenticate github user to odoo. Thus helping github
                user to login on odoo with Github User ID. When user login with Github, 
    """,
    'description': """
                    Github Odoo oauth provider
                    Odoo Github Oauth
                    Odoo github connector
                    Odoo Github project integration
                    Odoo github generic connector
                    Odoo modules to integrate
                    Odoo Github integration
                    Github+Odoo integration
                    Odoo Github
                    Github Odoo login
                    Odoo Github authentication
                    Github login on Odoo
    """,

    'author': "Ksolves India Ltd.",
    'website': "https://store.ksolves.com/",
    'category': 'Sales',
    'version': '15.0.1.0.0',
    'application': True,
    'license': 'LGPL-3',
    'currency': 'EUR',
    'price': 0.0,
    'maintainer': 'Ksolves India Ltd.',
    'support': 'sales@ksolves.com',
    'images': ['static/description/banner.gif'],
    'depends': ['auth_oauth'],
    # any module necessary for this one to work correctly
    'data': [
        'data/ks_auth.xml',
        # 'views/ks_res_users_views.xml',
        'views/ks_oauth_providers_views.xml',
    ]
}
