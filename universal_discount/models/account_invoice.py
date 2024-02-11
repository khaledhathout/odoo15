from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class KsGlobalDiscountInvoice(models.Model):
    # _inherit = "account.invoice"
    """ changing the model to account.move """
    _inherit = "account.move"


    ks_global_discount_type = fields.Selection([
        ('percent', 'Percentage'),
        ('amount', 'Amount')],
        string='Universal Discount Type',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
        default='percent')

    ks_global_discount_rate = fields.Float('Universal Discount',
                                           readonly=True,
                                           states={'draft': [('readonly', False)],
                                                   'sent': [('readonly', False)]})
    ks_amount_discount = fields.Monetary(string='Universal Discount',
                                         readonly=True,
                                         compute='ks_calculate_discount',
                                         store=True, track_visibility='always')

    ks_enable_discount = fields.Boolean(compute='ks_verify_discount')

    ks_sales_discount_account_id = fields.Integer(compute='ks_verify_discount')

    ks_purchase_discount_account_id = fields.Integer(compute='ks_verify_discount')
    global_discount = fields.Boolean(compute='ks_update_universal_discount')
    @api.depends('company_id.ks_enable_discount')
    def ks_verify_discount(self):
        for rec in self:
            rec.ks_enable_discount = rec.company_id.ks_enable_discount
            rec.ks_sales_discount_account_id = rec.company_id.ks_sales_discount_account.id
            rec.ks_purchase_discount_account_id = rec.company_id.ks_purchase_discount_account.id

    # 1. tax_line_ids is replaced with tax_line_id. 2. api.multi is also removed.

    # @api.multi
    @api.depends(
        'ks_global_discount_type',
        'ks_global_discount_rate',
        'amount_untaxed')
    def ks_calculate_discount(self):
        for rec in self:
            if rec.ks_global_discount_type == "amount":
                rec.ks_amount_discount = rec.ks_global_discount_rate if rec.amount_untaxed > 0 else 0
            elif rec.ks_global_discount_type == "percent":
                if rec.ks_global_discount_rate != 0.0:
                    rec.ks_amount_discount = (rec.amount_untaxed+rec.) * rec.ks_global_discount_rate / 100
                else:
                    rec.ks_amount_discount = 0
            elif not rec.ks_global_discount_type:
                rec.ks_global_discount_rate = 0
                rec.ks_amount_discount = 0

    @api.constrains('ks_global_discount_rate')
    def ks_check_discount_value(self):
        if self.ks_global_discount_type == "percent":
            if self.ks_global_discount_rate > 100 or self.ks_global_discount_rate < 0:
                raise ValidationError('You cannot enter percentage value greater than 100.')
        else:
            if self.ks_global_discount_rate < 0 or self.amount_untaxed < 0:
                raise ValidationError(
                    'You cannot enter discount amount greater than actual cost or value lower than 0.')

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        ks_res = super(KsGlobalDiscountInvoice, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                                      description=None, journal_id=None)
        ks_res['ks_global_discount_rate'] = self.ks_global_discount_rate
        ks_res['ks_global_discount_type'] = self.ks_global_discount_type
        return ks_res

    @api.depends('ks_amount_discount')
    def ks_update_universal_discount(self):
        """This Function Updates the Universal Discount through Sale Order"""
        for rec in self:
            rec.global_discount = True
            if rec.ks_global_discount_type and rec.ks_amount_discount>0:
                taxes = rec.invoice_line_ids.mapped('tax_ids')
                exist_rec = rec.invoice_line_ids.filtered(lambda l: l.global_discount)
                #raise UserError(exist_rec.price_unit)
                if exist_rec:
                    exist_rec.price_unit= rec.ks_amount_discount
                else:
                    rec.invoice_line_ids =[(0,0,({
                            'account_id': rec.ks_purchase_discount_account_id,
                            'quantity': -1,
                            'price_unit': rec.ks_amount_discount,
                            'tax_ids':taxes,
                            'global_discount':True
                        }))]

                for line in rec.invoice_line_ids:
                    line._onchange_price_subtotal()
                rec._compute_amount()

                rec._recompute_dynamic_lines(recompute_all_taxes=True)
                rec._compute_tax_totals_json()


class KsGlobalDiscountInvoiceLine(models.Model):
    # _inherit = "account.invoice"
    """ changing the model to account.move """
    _inherit = "account.move.line"

    global_discount = fields.Boolean(string="Global Discount")
