# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models


class SHAccountMove(models.Model):
    _inherit = "account.move"

    sh_invoice_quantity = fields.Float(
        string='No. Invoice Quantity', compute="_compute_invoiced_quantity")

    sh_invoice_config = fields.Boolean(
        'Enable Total number of Qty in Sale order', related='company_id.sh_invoice_config')

    sh_print_invoice_config = fields.Boolean(
        'Print Total number of Qty In Invoice Report', related='company_id.sh_print_invoice_config')

    @api.depends('invoice_line_ids.quantity')
    def _compute_invoiced_quantity(self):
        for rec in self:
            total_invoice_quantity = 0
            for line in rec.invoice_line_ids:
                if line.product_id:
                    total_invoice_quantity += line.quantity
            rec.sh_invoice_quantity = total_invoice_quantity
