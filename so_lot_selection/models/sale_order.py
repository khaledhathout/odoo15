# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        lot_lines = self.order_line.filtered(lambda l: l.lot_id)
        for line in lot_lines:
            lot_quants = line.lot_id.quant_ids.filtered(lambda l: l.location_id==self.warehouse_id.lot_stock_id).mapped('available_quantity')

            lot_qty = sum(q for q in lot_quants)

            demand_qty = sum(x for x in self.order_line.filtered(lambda l: l.lot_id.id == line.lot_id.id).mapped('product_uom_qty'))

            if demand_qty > lot_qty:
                raise UserError(_("Stock Quantity Not Available In Lot %s Number ") % (line.lot_id.name))
        return super().action_confirm()



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_id = fields.Many2one('stock.production.lot', string="Lot", domain="[('product_id','=',product_id)]")
