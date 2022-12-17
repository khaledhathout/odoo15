# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class TenancyDetails(models.Model):
    _name = 'tenancy.details'
    _description = 'Information Related To customer Tenancy while Creating Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'tenancy_seq'

    tenancy_seq = fields.Char(string='Sequence', required=True, readonly=True, default=lambda self: ('New'))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    close_contract_state = fields.Boolean(string='Contract State')
    active_contract_state = fields.Boolean(string='Active State')
    is_extended = fields.Boolean(string='Extended')
    contract_type = fields.Selection([('new_contract', 'Draft'),
                                      ('running_contract', 'Running'),
                                      ('cancel_contract', 'Cancel'),
                                      ('close_contract', 'Close'),
                                      ('expire_contract', 'Expire')],
                                     string='Contract Type')

    # Tenancy Information
    tenancy_id = fields.Many2one('res.partner', string='Tenant', domain=[('user_type', '=', 'customer')])
    is_any_broker = fields.Boolean(string='Any Broker')
    broker_id = fields.Many2one('res.partner', string='Broker', domain=[('user_type', '=', 'broker')])
    commission = fields.Monetary(related='broker_id.broker_commission', string='Commission')
    last_invoice_payment_date = fields.Date(string='Last Invoice Payment Date')
    broker_invoice_state = fields.Boolean(string='Broker  invoice State')
    broker_invoice_id = fields.Many2one('account.move', string='Bill')
    term_condition = fields.Html(string='Term and Condition')

    # Property Information
    property_id = fields.Many2one('property.details', string='Property', domain=[('stage', '=', 'available')])
    property_landlord_id = fields.Many2one(related='property_id.landlord_id', string='Landlord')
    property_type = fields.Selection(related='property_id.type', string='Type')
    total_rent = fields.Monetary(string='Rent')

    # Time Period
    payment_term = fields.Selection([('monthly', 'Monthly'),
                                     ('full_payment', 'Full Payment')],
                                    string='Payment Term')
    duration_id = fields.Many2one('contract.duration', string='Duration')
    contract_agreement = fields.Binary(string='Contract Agreement')
    file_name = fields.Char(string='File Name')
    month = fields.Integer(related='duration_id.month', string='Month')
    start_date = fields.Date(string='Start Date', default=fields.date.today())
    end_date = fields.Date(string='End Date', compute='_compute_end_date')

    # Related Field
    rent_invoice_ids = fields.One2many('rent.invoice', 'tenancy_id', string='Invoices')

    # Sequence Create
    @api.model
    def create(self, vals):
        if vals.get('tenancy_seq', ('New')) == ('New'):
            vals['tenancy_seq'] = self.env['ir.sequence'].next_by_code(
                'tenancy.details') or ('New')
        res = super(TenancyDetails, self).create(vals)
        return res

    @api.depends('start_date', 'month')
    def _compute_end_date(self):
        end_date = fields.date.today()
        for rec in self:
            end_date = rec.start_date + relativedelta(months=rec.month)
            rec.end_date = end_date

    # Smart Button
    invoice_count = fields.Integer(string='Invoice Count', compute="_compute_invoice_count")

    @api.depends('rent_invoice_ids')
    def _compute_invoice_count(self):
        for rec in self:
            count = self.env['rent.invoice'].search_count([('tenancy_id', '=', rec.id)])
            rec.invoice_count = count

    def action_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'rent.invoice',
            'domain': [('tenancy_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current'
        }

    # Button 
    def action_close_contract(self):
        self.close_contract_state = True
        self.property_id.write({'stage': 'available'})
        self.contract_type = 'close_contract'
        return True

    def action_active_contract(self):
        self.contract_type = 'running_contract'
        self.active_contract_state = True
        record = {
            'product_id': self.env.ref('rental_management.property_product_1').id,
            'name': 'First Invoice of ' + self.property_id.name,
            'quantity': 1,
            'price_unit': self.total_rent
        }
        invoice_lines = [(0, 0, record)]
        data = {
            'partner_id': self.tenancy_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines
        }
        invoice_id = self.env['account.move'].sudo().create(data)
        invoice_id.action_post()
        self.last_invoice_payment_date = invoice_id.invoice_date

        rent_invoice = {
            'tenancy_id': self.id,
            'type': 'rent',
            'invoice_date': fields.Date.today(),
            'description': 'First Rent',
            'rent_invoice_id': invoice_id.id
        }
        self.env['rent.invoice'].create(rent_invoice)
        return True

    def action_cancel_contract(self):
        self.close_contract_state = True
        self.property_id.write({'stage': 'available'})
        self.contract_type = 'cancel_contract'

    def action_broker_invoice(self):
        record = {
            'product_id': self.env.ref('rental_management.property_product_1').id,
            'name': 'Brokerage of ' + self.property_id.name,
            'quantity': 1,
            'price_unit': self.commission
        }
        invoice_lines = [(0, 0, record)]
        data = {
            'partner_id': self.broker_id.id,
            'move_type': 'in_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines
        }
        invoice_id = self.env['account.move'].sudo().create(data)
        invoice_id.action_post()
        self.broker_invoice_state = True
        self.broker_invoice_id = invoice_id.id
        return True

    @api.model
    def tenancy_recurring_invoice(self):
        today_date = fields.Date.today()
        tenancy_contracts = self.env['tenancy.details'].sudo().search(
            [('contract_type', '=', 'running_contract'), ('payment_term', '=', 'monthly')])
        for rec in tenancy_contracts:
            if rec.contract_type == 'running_contract' and rec.payment_term == 'monthly':
                if today_date < rec.end_date:
                    days = (today_date - rec.last_invoice_payment_date).days
                    if days >= 30:
                        print("Scheduler run")
                        record = {
                            'product_id': self.env.ref('rental_management.property_product_1').id,
                            'name': 'Installment of ' + rec.property_id.name,
                            'quantity': 1,
                            'price_unit': rec.total_rent
                        }
                        invoice_lines = [(0, 0, record)]
                        data = {
                            'partner_id': rec.tenancy_id.id,
                            'move_type': 'out_invoice',
                            'invoice_date': today_date,
                            'invoice_line_ids': invoice_lines
                        }
                        invoice_id = self.env['account.move'].sudo().create(data)
                        invoice_id.action_post()
                        rec.last_invoice_payment_date = invoice_id.invoice_date

                        rent_invoice = {
                            'tenancy_id': rec.id,
                            'type': 'rent',
                            'invoice_date': fields.Date.today(),
                            'description': 'Installment of ' + rec.property_id.name,
                            'rent_invoice_id': invoice_id.id
                        }
                        self.env['rent.invoice'].create(rent_invoice)
            #         else:
            #             print('Not 30 Days')
            #     else:
            #         print('Contract is Over')
            # else:
            #     print('Not running or Monthly contract')
        return True

    @api.model
    def tenancy_expire(self):
        today_date = fields.Date.today()
        tenancy_contracts = self.env['tenancy.details'].sudo().search(
            [('contract_type', '=', 'running_contract'), ('payment_term', '=', 'monthly')])
        for rec in tenancy_contracts:
            if rec.contract_type == 'running_contract':
                if today_date > rec.end_date:
                    rec.contract_type = 'expire_contract'
            #     else:
            #         print('Not expire')
            # else:
            #     print('Not in Running')
        return True


class ContractDuration(models.Model):
    _name = 'contract.duration'
    _description = 'Contract Duration and Month'
    _rec_name = 'duration'

    duration = fields.Char(string='Duration', required=True)
    month = fields.Integer(string='Month')
