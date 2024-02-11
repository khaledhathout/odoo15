# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_return_invoice_policy = fields.Selection(
        [('order', 'Invoice what is ordered to return'),
         ('delivery', 'Invoice what is received')
         ], 'Sale Return Invoicing Policy', default='order'
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_return_invoice_policy = fields.Selection(
        related='company_id.sale_return_invoice_policy',
        string='Sale Return Invoicing Policy', readonly=False,

    )

    return_period = fields.Integer(
        default=3, config_parameter='sale_return_period'
    )
    exchange_period = fields.Integer(
        default=7, config_parameter='sale_exchange_period'
    )