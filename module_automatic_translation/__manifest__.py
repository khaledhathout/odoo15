# -*- coding: utf-8 -*-
{
    'name': "Automatic Translation Tool",
    'summary': """module automatic translation, Po Files Translator, odoo custom module translator, po file translator, i18n directory automatic creation, i18n automatic creation,Localize Odoo applications, custom module translator, Module translation, Google translator, automatic module translation, Google translation, Bing translator, Bing translation, Automatic translataion, Auto Translate Po Generator,Odoo Translation to any language,Translate Tool For translate any custom application within seconds,Translate texts with the help of Google Translate,Button To Translate New Words Using 'googletrans',Easy Translator All Odoo field, one click odoo translate, field char translator, field text translator, field html translator, with Bing, Google, ChatGPT Translate, or any other ai, PO file translate for all language,Web Language Translator,Translate base odoo file '.po' with the help of Google Translate,Translation Helper,Odoo Translation, Auto Translate Po Generator, Translate Odoo modules, Google and Bing translation, Po file generation, Translated content, Translation tool,Convenient translation,Language localization, automatic translation, """,
    'description': """Use an automated translation wizard to translate any module into any language, then create a Po file that already has the translation contained in the module.""",
    'author': "Khaled Hassan",
    'website': "https://apps.odoo.com/apps/modules/browse?search=Khaled+hassan",
    'category': 'Extra Tools',
    'version': '15.0',
    'depends': ['base'],
    'license': 'OPL-1',
    'currency': 'EUR',
    'images': ['static/description/main_screenshot.png'],
    'price': '150',
    'data': [
        'security/ir.model.access.csv',
        'wizard/translation_wizard_view.xml',
        'views/settings_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
