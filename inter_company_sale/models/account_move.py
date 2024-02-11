# Copyright 2020 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009
from __future__ import division
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import decimal


class AccountMove(models.Model):
    _inherit = 'account.move'

    # -------------------------------------------------------------------------
    # COGS METHODS
    # -------------------------------------------------------------------------
    @api.model
    def create(self,vals):
        res = super(AccountMove,self).create(vals)
        
        #raise UserError(res.invoice_line_ids)
        company = self.env['res.company'].search([('partner_id', '=',res.partner_id.id)], limit=1)
        if company and res.move_type=='out_invoice':
            for line in res.invoice_line_ids:
                accounts = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=res.fiscal_position_id)
                debit_interim_account = accounts['stock_output']
                line.account_id=debit_interim_account
        return res


    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        res  = super(AccountMove,self)._stock_account_prepare_anglo_saxon_out_lines_vals()
        for move in self:
            company = self.env['res.company'].search([('partner_id', '=',move.partner_id.id)], limit=1)
            if company and move.move_type=='out_invoice':
                return [] 
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    @api.onchange('product_id')
    def _onchange_product_id_account(self):
        #Inter company Transaction condition
        company = self.env['res.company'].search([('partner_id', '=',self.move_id.partner_id.id)], limit=1)

        if self.product_id and company and self.move_id.move_type=='out_invoice':
            accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=self.move_id.fiscal_position_id)
            debit_interim_account = accounts['stock_output']
            if debit_interim_account:
                self.account_id=debit_interim_account.id
                price_unit = self._stock_account_get_anglo_saxon_price_unit()
                self.price_unit=price_unit
    # default price must equal cost price

