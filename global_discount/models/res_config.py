from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    enable_sale_discount = fields.Boolean(string="Activate Sales Universal Discount")
    enable_purchase_discount = fields.Boolean(string="Activate Purchase Universal Discount")
    sales_discount_account = fields.Many2one('account.account', string="Sales Discount Account")
    purchase_discount_account = fields.Many2one('account.account', string="Purchase Discount Account")


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_sale_discount = fields.Boolean(string="Activate Sales Universal Discount", related='company_id.enable_sale_discount', readonly=False)
    enable_purchase_discount = fields.Boolean(string="Activate Purchase Universal Discount", related='company_id.enable_purchase_discount', readonly=False)

    sales_discount_account = fields.Many2one('account.account', string="Sales Discount Account", related='company_id.sales_discount_account', readonly=False)
    purchase_discount_account = fields.Many2one('account.account', string="Purchase Discount Account", related='company_id.purchase_discount_account', readonly=False)
