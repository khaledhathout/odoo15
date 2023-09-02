from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_demand_qty = fields.Float("Total Demand Qty", compute='set_total_qty')
    total_delivery_qty = fields.Float("Total Delivery Qty", compute='set_total_qty')
    total_invoice_qty = fields.Float("Total Invoice Qty", compute='set_total_qty')
    remaining_delivery_qty = fields.Float("Remaining Delivery Qty", compute='set_total_qty')
    pending_invoice_qty = fields.Float("Pending Invoice Qty", compute='set_total_qty')

    def set_total_qty(self):
        
        for order in self:
            order.total_demand_qty = order.order_line.mapped('product_uom_qty') and sum(order.order_line.mapped('product_uom_qty'))
            order.total_delivery_qty = order.order_line.mapped('qty_delivered') and sum(order.order_line.mapped('qty_delivered'))
            order.total_invoice_qty = order.order_line.mapped('qty_invoiced') and sum(order.order_line.mapped('qty_invoiced'))
            order.remaining_delivery_qty = order.total_demand_qty - order.total_delivery_qty
            order.pending_invoice_qty = order.total_demand_qty - order.total_invoice_qty

        return True
