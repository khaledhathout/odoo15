# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ContractWizard(models.TransientModel):
    _name = 'contract.wizard'
    _description = 'Create Contract of rent in property'

    # Tenancy
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('user_type', '=', 'customer')])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')

    # Property Details
    property_id = fields.Many2one('property.details', string='Property')
    total_rent = fields.Monetary(related='property_id.tenancy_price', string='Related')
    payment_term = fields.Selection([('monthly', 'Monthly'),
                                     ('full_payment', 'Full Payment')],
                                    string='Payment Term')
    is_any_broker = fields.Boolean(string='Any Broker?')
    broker_id = fields.Many2one('res.partner', string='Broker', domain=[('user_type', '=', 'broker')])
    duration_id = fields.Many2one('contract.duration', string='Duration')
    start_date = fields.Date(string='Start Date')

    def contract_action(self):
        if self.payment_term == 'monthly':
            self.customer_id.is_tenancy = True
            record = {
                'tenancy_id': self.customer_id.id,
                'property_id': self.property_id.id,
                'is_any_broker': self.is_any_broker,
                'broker_id': self.broker_id.id,
                'duration_id': self.duration_id.id,
                'start_date': self.start_date,
                'total_rent': self.total_rent,
                'contract_type': 'new_contract',
                'payment_term': self.payment_term
            }
            contract_id = self.env['tenancy.details'].create(record)

            data = {
                'stage': 'on_lease'
            }
            self.property_id.write(data)
        else:
            record = {
                'tenancy_id': self.customer_id.id,
                'property_id': self.property_id.id,
                'is_any_broker': self.is_any_broker,
                'broker_id': self.broker_id.id,
                'duration_id': self.duration_id.id,
                'start_date': self.start_date,
                'total_rent': self.total_rent,
                'contract_type': 'running_contract',
                'last_invoice_payment_date': fields.Date.today(),
                'payment_term': self.payment_term,
                'active_contract_state': True
            }
            contract_id = self.env['tenancy.details'].create(record)

            data = {
                'stage': 'on_lease'
            }
            self.property_id.write(data)

            # Creating Invoice
            amount = self.property_id.tenancy_price
            total_amount = amount * self.duration_id.month
            full_payment_record = {
                'product_id': self.env.ref('rental_management.property_product_1').id,
                'name': 'Full Payment of ' + self.property_id.name,
                'quantity': 1,
                'price_unit': total_amount
            }
            invoice_lines = [(0, 0, full_payment_record)]
            data = {
                'partner_id': self.customer_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.date.today(),
                'invoice_line_ids': invoice_lines
            }
            invoice_id = self.env['account.move'].sudo().create(data)
            invoice_id.action_post()

            rent_invoice = {
                'tenancy_id': contract_id.id,
                'type': 'full_rent',
                'invoice_date': fields.date.today(),
                'amount': total_amount,
                'description': 'Full Payment Of Rent',
                'rent_invoice_id': invoice_id.id
            }
            rent_invoice_id = self.env['rent.invoice'].create(rent_invoice)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Contract',
            'res_model': 'tenancy.details',
            'res_id': contract_id.id,
            'view_mode': 'form,tree',
            'target': 'current'
        }
