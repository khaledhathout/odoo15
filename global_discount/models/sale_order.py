from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree
import json
class GlobalDiscountSo(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self,vals):
        if 'amount_discout' in vals and vals['amount_discount']:

            self = self.with_context(skip_recompute=True)

        return super(GlobalDiscountSo,self).create(vals)

    global_discount_type = fields.Selection([
        ('percent', 'Percentage'),
        ('amount', 'Amount')],
        string='Universal Discount Type',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
        default='percent')

    global_discount_rate = fields.Float('Universal Discount',
                                           readonly=True,
                                           states={'draft': [('readonly', False)],
                                                   'sent': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Universal Discount',track_visibility='always')

    enable_sale_discount = fields.Boolean(compute='verify_discount')

    @api.depends('company_id.enable_sale_discount')
    def verify_discount(self):
        for rec in self:
            rec.enable_sale_discount = rec.company_id.enable_sale_discount


    @api.onchange(
        'global_discount_type',
        'global_discount_rate',
        'amount_untaxed','order_line')
    def calculate_discount_amount(self):
        for rec in self:
            rec.reset_discount_line()            
            if rec.global_discount_type == "amount":
                rec.amount_discount = rec.global_discount_rate if rec.amount_untaxed > 0 else 0
            elif rec.global_discount_type == "percent":
                if rec.global_discount_rate != 0.0:
                    rec.amount_discount = (rec.amount_untaxed) * rec.global_discount_rate / 100
                else:
                    rec.amount_discount = 0
            elif not rec.global_discount_type:
                rec.global_discount_rate = 0
                rec.amount_discount = 0
            #if rec.amount_discount != 0:    
            rec.recalculate_discount_line()

    def reset_discount_line(self):
        for rec in self:
            discount_line = rec.order_line.filtered(lambda l:l.global_discount)
            if discount_line and not self._context.get('skip_recompute'):
                rec.order_line = [(2,discount_line.id)]

    def recalculate_discount_line(self):
        for rec in self:
            if rec.amount_discount !=0 and not self._context.get('skip_recompute'):
                line = []
                line.append((0,0,{
                    'product_uom_qty':1,
                    'product_id':rec.get_global_discount_product_id(),
                    'global_discount':True                
                    }))

                rec.order_line = line
                discount_line = rec.order_line.filtered(lambda l:l.global_discount)[0]
                discount_line.product_id_change()

                if discount_line :
                    discount_line.update({'price_unit':-rec.amount_discount})

    def _create_invoices(self, grouped=False, final=False, date=None):
        if self.global_discount_rate>0:
            self=self.with_context(set_universal_line=True)
        return super(GlobalDiscountSo,self)._create_invoices(grouped=grouped, final=final, date=date)

    def _prepare_invoice(self):
        ks_res = super(GlobalDiscountSo, self)._prepare_invoice()
        ks_res['global_discount_type'] = self.global_discount_type
        ks_res['global_discount_rate'] = self.global_discount_rate
        ks_res['amount_discount'] = self.amount_discount

        return ks_res
                
    def get_global_discount_product_id(self):
        product_id = self.env['product.product'].search([('detailed_type','!=','product'),('global_discount','=',True)])
        if not product_id:
            vals = self._prepare_deposit_product()
            product_id = self.env['product.product'].create(vals)

        return product_id

    def _prepare_deposit_product(self):
        return {
            'active':True,
            'name': 'Universal Discount',
            'type': 'service',
            'invoice_policy': 'order',
            'property_account_income_id': self.company_id.sales_discount_account.id,
            'property_account_expense_id': self.company_id.purchase_discount_account.id,
            'global_discount':True,
            'company_id': False,
        }

    @api.constrains('global_discount_rate')
    def ks_check_discount_value(self):
        if self.global_discount_type == "percent":
            if self.global_discount_rate > 100 or self.global_discount_rate < 0:
                raise ValidationError('You cannot enter percentage value greater than 100.')
        else:
            if self.global_discount_rate < 0 or self.amount_untaxed < 0:
                raise ValidationError(
                    'You cannot enter discount amount greater than 1 actual cost or value lower than 0.')

class GlobalDiscountSoLine(models.Model):
    _inherit = "sale.order.line"

    global_discount = fields.Boolean(string="Global Discount")
    
    def _prepare_invoice_line(self, **optional_values):
        res= super(GlobalDiscountSoLine,self)._prepare_invoice_line()
        if self.global_discount:
            res['global_discount'] = True
            res['account_id'] = self.product_id.property_account_income_id.id
        return res

    @api.model
    def _where_calc(self, domain, active_test=True):
        if self.env.context.get('commit_assetsbundle'):        
            domain= domain+ [('global_discount','=',False)]
        return super(GlobalDiscountSoLine,self)._where_calc(domain, active_test=active_test)