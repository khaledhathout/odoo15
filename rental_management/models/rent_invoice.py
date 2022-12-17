# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class RentInvoice(models.Model):
    _name = 'rent.invoice'
    _description = 'Crete Invoice for Rented property'
    _rec_name = 'tenancy_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    tenancy_id = fields.Many2one('tenancy.details', string='Tenancy No.')
    customer_id = fields.Many2one(related='tenancy_id.tenancy_id', string='Customer')
    type = fields.Selection([('deposit', 'Deposit'),
                             ('rent', 'Rent'),
                             ('maintenance', 'Maintenance'),
                             ('penalty', 'Penalty'),
                             ('full_rent', 'Full Rent')],
                            string='Payment', default='rent')
    invoice_date = fields.Date(string='Invoice Date')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    rent_amount = fields.Monetary(string='Rent Amount', related='tenancy_id.total_rent')
    amount = fields.Monetary(string='Amount')
    description = fields.Char(string='Description')
    rent_invoice_id = fields.Many2one('account.move', string='Invoice')
