# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError, Warning, ValidationError

from odoo.exceptions import UserError
import base64
import logging
_logger = logging.getLogger("logger===========")


class Sale(models.Model):
    _inherit = 'sale.order'

    approved_date = fields.Datetime(string='Approved Date', readonly=True)


    @api.model
    def get_purchase_done(self):
        search_id = self.env['sale.order'].search([('state', '=', 'sale'), ('purchase_done', '=', False)])
        for res in search_id:
            purchase_ = self.env['purchase.order'].search([
                ('opportunity_id', '=', res.opportunity_id.id)])
            list_ = []
            for data in purchase_:
                if data.state == 'purchase':
                    list_.append(True)
                if data.state not in ('purchase', 'cancel'):
                    list_.append(False)
            if False in list_ or not list_:
                res.purchase_done = False
            else:
                res.purchase_done = True

    def _prepare_invoice(self):
        res = super(Sale, self)._prepare_invoice()

        res.update({
            'opportunity_id': self.opportunity_id.id,
            'opportunity_flow': self.opportunity_flow,
            'approved_date': self.approved_date,

        })
        return res

    def _create_invoices(self, grouped=False, final=False):
        rec = super(Sale, self)._create_invoices(grouped, final)
        invoice_id = self.env['account.move'].search([('id', '=', rec[0].id)])
        # invoice_id.opportunity_id = self.opportunity_id.id
        # invoice_id.opportunity_flow = self.opportunity_flow
        invoice_id.approved_date = self.approved_date
        # atr13
        invoice_id.customer_po = self.client_order_ref

        return rec


    def action_confirm(self):
        obj = super(Sale, self).action_confirm()
        if self and not self.client_order_ref:
            raise UserError(_('Please fill the customer reference number!'))
        self.approved_date = datetime.now()
        return obj

    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env.ref('sale.action_report_saleorder').report_action(self)

    def _compute_is_expired(self):
        today = fields.Date.today()
        for order in self:
            order.is_expired = order.state in ('sent','draft') and order.validity_date and order.validity_date < today

    amount_untaxed = fields.Float(compute='_amount_all', store=True)
    amount_tax = fields.Float(compute='_amount_all', store=True)
    amount_total = fields.Float(compute='_amount_all', store=True)

    def has_to_be_signed(self, include_draft=True):
        return (self.state == 'sent' or (self.state == 'draft' and include_draft)) and not self.is_expired and self.require_signature and not self.signature

    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False

        if force_confirmation_template or (self.state != 'sales' and not self.env.context.get('proforma', False)):
            template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
            template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
            if not template_id:
                template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.mail_template_sale_confirmation', raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data']._xmlid_to_res_id('sale.email_template_edi_sale', raise_if_not_found=False)

        return template_id

    def _prepare_invoice(self):
        res = super(Sale, self)._prepare_invoice()
        res.update({'tag_ids': [(6, 0, self.tag_ids.ids)]})
        return res

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=False):
        """Override for sales order.

        If the SO is in a state where an action is required from the partner,
        return the URL with a login token. Otherwise, return the URL with a
        generic access token (no login).
        """
        self.ensure_one()
        if self.state not in ['sale', 'done']:
            return self.get_portal_url()
        return super(Sale, self)._get_share_url(redirect, signup_partner, pid)


class InvoiceLine(models.Model):
    _inherit = 'sale.order.line'

    # price_subtotal = fields.Float(compute='_compute_amount')
    price_tax = fields.Float(compute='_compute_amount')
    price_total = fields.Float(compute='_compute_amount')

 # atr10
class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_invoice_lines(self):
        invoice_lines = self.invoice_line_ids.sorted('sequence')

        return invoice_lines

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=False):
        """Override for Invoice.

        If the SO is in a state where an action is required from the partner,
        return the URL with a login token. Otherwise, return the URL with a
        generic access token (no login).
        """
        self.ensure_one()
        if self.state != 'posted':
            return self.get_portal_url()
        return super(AccountMove, self)._get_share_url(redirect, signup_partner, pid)




