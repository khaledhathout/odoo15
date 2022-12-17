# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Advanced Property Sale & Rental Management | Real Estate | Property Sales | Property Rental",
    'description': """
        - Property Sale
        - Property Rental
        - Lease Contract
        - Lanlord Management
        - Customer Management
        - Property Maintance
        - Customer Recurring Invoice
        - Property List
    """,
    'summary': """
        Property Sale & Rental Management
    """,
    'version': "1.0",
    'author': 'TechKhedut Inc.',
    'company': 'TechKhedut Inc.',
    'maintainer': 'TechKhedut Inc.',
    'website': "https://www.techkhedut.com",
    'category': 'Industry',
    'depends': ['mail', 'contacts', 'account', 'hr', 'maintenance'],
    'data': [
        # security
        'security/groups.xml',
        'security/ir.model.access.csv',
        # Data
        'data/ir_cron.xml',
        'data/sequence.xml',
        'data/property_product_data.xml',
        # wizard views
        'wizard/contract_wizard_view.xml',
        'wizard/property_payment_wizard_view.xml',
        'wizard/extend_contract_wizard_view.xml',
        'wizard/property_vendor_wizard_view.xml',
        'wizard/property_maintenance_wizard_view.xml',
        # Views
        'views/assets.xml',
        'views/property_details_view.xml',
        'views/property_document_view.xml',
        'views/user_type_view.xml',
        'views/tenancy_details_view.xml',
        'views/contract_duration_view.xml',
        'views/rent_invoice_view.xml',
        'views/property_amenities_view.xml',
        'views/property_specification_view.xml',
        'views/property_vendor_view.xml',
        'views/certificate_type_view.xml',
        'views/parent_property_view.xml',
        'views/property_tag_view.xml',
        # Inherit Views
        'views/maintenance_product_inherit.xml',
        'views/property_maintenance_view.xml',
        # Report views
        'report/tenancy_details_report_template.xml',
        # menus
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'rental_management/static/src/xml/template.xml',
        ],
        'web.assets_backend': [
            'rental_management/static/src/css/lib/style.css',
            'rental_management/static/src/css/style.scss',
            'rental_management/static/src/js/rental.js',
        ],
    },
    'images': [
        'static/description/property-rental.gif',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 199,
    'currency': 'USD',
}
