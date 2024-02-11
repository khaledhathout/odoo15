# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    """"""
    _inherit = "product.template"

    is_free_temp = fields.Boolean('is Free')

    @api.model
    def create(self, vals_list):
        res = super(ProductTemplate, self).create(vals_list)
        products = self.env['product.product'].search([('product_tmpl_id', '=', res.id)])
        if products:
            for product in products:
                product.is_free = True if res.is_free_temp == True else False
        return res

    def write(self, vals_list):
        res = super(ProductTemplate, self).write(vals_list)
        products = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        if products:
            for product in products:
                product.is_free = vals_list.get('is_free_temp')
        return res

class ProductProduct(models.Model):
    """"""
    _inherit = "product.product"

    is_free = fields.Boolean('is Free')

class PurchaseOrderLine(models.Model):
    """"""
    _inherit = "purchase.order.line"

    free_product = fields.Boolean("Free Product", default=False)

    @api.onchange('product_id')
    def check_free_product(self):
        self.free_product = False
        if self.product_id.is_free:
            self.free_product = True
