# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class PropertyVendor(models.Model):
    _name = 'property.vendor'
    _description = 'Stored Data About Sold Property'
    _rec_name = 'sold_seq'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sold_seq = fields.Char(string='Sequence', required=True, readonly=True, default=lambda self: ('New'))
    stage = fields.Selection([('booked', 'Booked'),
                              ('refund', 'Refund'),
                              ('sold', 'Sold')], string='Stage')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    sold_document = fields.Binary(string='Sold Document')
    file_name = fields.Char('File Name')
    term_condition = fields.Html(string='Term and Condition')

    # Broker and Customer

    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('user_type', '=', 'customer')])
    is_any_broker = fields.Boolean(string='Any Broker')
    broker_id = fields.Many2one('res.partner', string='Broker', domain=[('user_type', '=', 'broker')])
    commission = fields.Monetary(related='broker_id.broker_commission', string='Commission')

    # Property Information
    property_id = fields.Many2one('property.details', string='Property', domain=[('stage', '=', 'sale')])
    book_price = fields.Monetary(related='property_id.token_amount', string='Book Price')
    sale_price = fields.Monetary(related='property_id.sale_price', string='Sale Price', store=True)
    ask_price = fields.Monetary(string='Ask Price')
    book_invoice_id = fields.Many2one('account.move', string='Advance', readonly=True)
    book_invoice_state = fields.Boolean(string='Invoice State')
    sold_invoice_id = fields.Many2one('account.move', string='Sold Invoice', readonly=True)
    sold_invoice_state = fields.Boolean(string='Sold Invoice State')

    @api.model
    def create(self, vals):
        if vals.get('sold_seq', ('New')) == ('New'):
            vals['sold_seq'] = self.env['ir.sequence'].next_by_code(
                'property.vendor') or ('New')
        res = super(PropertyVendor, self).create(vals)
        return res

    def name_get(self):
        data = []
        for rec in self:
            data.append((rec.id, '%s - %s' % (rec.sold_seq, rec.customer_id.name)))
        return data

    def action_book_invoice(self):
        record = {
            'product_id': self.env.ref('rental_management.property_product_1').id,
            'name': 'Booked Amount of   ' + self.property_id.name,
            'quantity': 1,
            'price_unit': self.book_price
        }
        invoice_lines = [(0, 0, record)]
        data = {
            'partner_id': self.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.date.today(),
            'invoice_line_ids': invoice_lines
        }
        book_invoice_id = self.env['account.move'].sudo().create(data)
        book_invoice_id.action_post()
        self.book_invoice_id = book_invoice_id.id
        self.book_invoice_state = True
        self.property_id.stage = 'booked'
        self.stage = 'booked'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booked Invoice',
            'res_model': 'account.move',
            'res_id': book_invoice_id.id,
            'view_mode': 'form,tree',
            'target': 'current'
        }
