# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class PropertySold(models.TransientModel):
    _name = 'property.vendor.wizard'
    _description = 'Wizard For Selecting Customer to sale'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    property_id = fields.Many2one('property.details', string='Property')
    customer_id = fields.Many2one('property.vendor', string='Customer')
    final_price = fields.Monetary(string='Price')
    sold_invoice_id = fields.Many2one('account.move')

    @api.onchange('customer_id')
    def drive_final_price(self):
        for rec in self:
            if rec.customer_id:
                final_price = rec.customer_id.ask_price
                rec.final_price = final_price
            else:
                rec.final_price = 0

    def property_vendor_action(self):
        self.customer_id.customer_id.is_sold_customer = True
        if self.customer_id.is_any_broker == True:
            broker_name = 'Commission of %s' % self.customer_id.broker_id.name
        else:
            broker_name = 'Broker Commission'

        final_price = self.final_price - self.customer_id.book_price
        record = {
            'product_id': self.env.ref('rental_management.property_product_1').id,
            'name': self.property_id.name,
            'quantity': 1,
            'price_unit': final_price
        }
        broker_record = {
            'product_id': self.env.ref('rental_management.property_product_1').id,
            'name': broker_name,
            'quantity': 1,
            'price_unit': self.customer_id.commission
        }
        invoice_lines = [(0, 0, record), (0, 0, broker_record)]
        data = {
            'partner_id': self.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.date.today(),
            'invoice_line_ids': invoice_lines
        }
        sold_invoice_id = self.env['account.move'].sudo().create(data)
        sold_invoice_id.action_post()
        self.sold_invoice_id = sold_invoice_id.id
        sold_record = {
            'sold_invoice_state': True,
            'sold_invoice_id': self.sold_invoice_id,
            'stage': 'sold'
        }
        self.customer_id.write(sold_record)
        self.property_id.write({'stage': 'sold', 'sold_invoice_id': self.sold_invoice_id, 'sold_invoice_state': True})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Booked Invoice',
            'res_model': 'account.move',
            'res_id': sold_invoice_id.id,
            'view_mode': 'form,tree',
            'target': 'current'
        }
