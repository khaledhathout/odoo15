# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models


class SHSaleOrder(models.Model):
    _inherit = "sale.order"

    sh_ordered_quantity = fields.Float(
        string='No. Ordered Quantity', compute="_compute_ordered_quantity")

    sh_invoiced_quantity = fields.Float(
        string='No. Invoiced Quantity', compute="_compute_invoiced_quantity")

    sh_sale_config = fields.Boolean(
        'Enable Total number of Qty in Sale order', related='company_id.sh_sale_config')

    sh_print_sale_config = fields.Boolean(
        'Print Total number of Qty In Sale Report', related='company_id.sh_print_sale_config')

    @api.depends('order_line.product_uom_qty')
    def _compute_ordered_quantity(self):
        for rec in self:
            total_ordered_quantity = 0
            for line in rec.order_line:
                if line.product_id:
                    total_ordered_quantity += line.product_uom_qty
            rec.sh_ordered_quantity = total_ordered_quantity

    @api.depends('order_line.qty_invoiced')
    def _compute_invoiced_quantity(self):
        for rec in self:
            total_invoiced_quantity = 0
            for line in rec.order_line:
                if line.product_id:
                    total_invoiced_quantity += line.qty_invoiced
            rec.sh_invoiced_quantity = total_invoiced_quantity
