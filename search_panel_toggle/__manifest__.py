# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2018 Bonainfo <guoyihot@outlook.com>
# All Rights Reserved
#
##############################################################################
{
    'author': 'Dmmsys 124358678@qq.com ',
    'website': 'www.bonainfo.com,www.dmmsys.com',
    'version': '15.0.1.1.0',
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'support': '124358678@qq.com, bower_guo@msn.com',
    'price': '0',
    'currency': 'EUR',
    'images': ['static/description/main_banner.png'],
   
    
    'name': 'Search Panel Hide & Show',
    'summary': """Enable search panel hide & show by a toggle button.""",
    'description': """Search panel hide & show
     
     List view search panel hide
     Kanban view search panel hide
    Colum Width,
    Page Size,
    Advance Dynamic Tree View ,
	Advance Search ,
	Best List View Apps ,
	Best Tree View Apps ,
    Dynamic List View,
    Dynamic List ,
    Dynamic Search ,
    Dynamic Column ,
	Dynamic List View Apps , 
	Drag and edit columns ,
    List View ,
    List View Manage ,
    List View Management ,
    List View Column ,
	List view Advance Search ,
	List View Apps ,
	List View Management Apps ,
	Listview ,
    Field Display Control ,
    Field Hide Show ,
	Freeze List View Header ,    
	Hide/Show list view columns ,
	Odoo List View ,
	Odoo Advanced Search ,
	Odoo Manage List View ,
	Tree View Apps ,    
	Tree/List View Apps  ,
	Tree view Advance Search ,
	Treeview ,
	Tree View ,     
     
    """,


    # any module necessary for this one to work correctly
    'depends': ['web', 'product'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'views/product_search_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'assets': {
        'web.assets_qweb': ['search_panel_toggle/static/src/**/*.xml'],
        'web.assets_backend': [
            'search_panel_toggle/static/src/css/search_panel_toggle.scss',
            'search_panel_toggle/static/src/js/search_panel_toggle.js',

        ],
    }
}
