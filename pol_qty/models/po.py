from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_demand_qty = fields.Float("Total Demand Qty", compute='set_total_qty')
    total_received_qty = fields.Float("Total Received Qty", compute='set_total_qty')
    total_billed_qty = fields.Float("Total Billed Qty", compute='set_total_qty')
    remaining_received_qty = fields.Float("Remaining Received Qty", compute='set_total_qty')
    pending_billed_qty = fields.Float("Pending Billed Qty", compute='set_total_qty')

    def set_total_qty(self):
        
        for order in self:
            order.total_demand_qty = order.order_line.mapped('product_qty') and sum(order.order_line.mapped('product_qty'))
            order.total_received_qty = order.order_line.mapped('qty_received') and sum(order.order_line.mapped('qty_received'))
            order.total_billed_qty = order.order_line.mapped('qty_invoiced') and sum(order.order_line.mapped('qty_invoiced'))
            order.remaining_received_qty = order.total_demand_qty - order.total_received_qty
            order.pending_billed_qty = order.total_demand_qty - order.total_billed_qty

        return True
