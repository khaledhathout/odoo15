from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    ks_enable_discount = fields.Boolean(string="Activate Universal Discount")
    ks_sales_discount_account = fields.Many2one('account.account', string="Sales Discount Account")
    ks_purchase_discount_account = fields.Many2one('account.account', string="Purchase Discount Account")


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_enable_discount = fields.Boolean(string="Activate Universal Discount", related='company_id.ks_enable_discount', readonly=False)
    ks_sales_discount_account = fields.Many2one('account.account', string="Sales Discount Account", related='company_id.ks_sales_discount_account', readonly=False)
    ks_purchase_discount_account = fields.Many2one('account.account', string="Purchase Discount Account", related='company_id.ks_purchase_discount_account', readonly=False)

class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()
        if self.env.context.get('discount'):
            base_amount=base_amount-self.env.context.get('discount')
            #s=s

        return super(AccountTax,self)._compute_amount(base_amount, price_unit, quantity=1.0, product=None, partner=None)