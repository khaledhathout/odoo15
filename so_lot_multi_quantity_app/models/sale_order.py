# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        move_id = self.picking_ids.mapped("move_ids_without_package")
        move_line_ids = move_id.mapped("move_line_ids")
        move_line_ids.write({'move_id':False})
        move_line_ids.unlink()
        for rec in self.order_line:
            if rec.lot_id:
                lot_id = round(int(rec.product_uom_qty) / len(rec.lot_id))
                move_id = self.picking_ids.mapped("move_ids_without_package")
                move_line_ids = move_id.mapped("move_line_ids")
                move_ids = move_id.filtered(lambda pro:pro.product_id == rec.product_id)
                move_ids.write({
                    'product_id' : rec.product_id.id,
                    'quantity_done' : 0.0,
                    'reserved_availability' : 0.0,
                    'product_uom_qty' : rec.product_uom_qty,
                    })
                vals_list = []
                for line in rec.lot_id:
                    if line.product_qty < lot_id:
                        raise UserError(_("Stock Not Found In Lot %s Number!!!")%(line.name))         
                    vals = {
                        'lot_id' : line.id,
                        'product_id' : rec.product_id.id,
                        'qty_done' : lot_id,
                        'product_uom_qty' : 0.0,
                        'location_id': move_ids.location_id.id,
                        'location_dest_id': move_ids.location_dest_id.id,
                        'product_uom_id' : rec.product_id.uom_id.id,
                        'move_id' : move_ids.id,
                        'picking_id':self.picking_ids.id
                    }
                    vals_list.append(vals)
                for val in vals_list:
                    move_id_data = self.env['stock.move.line'].create(val)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    lot_id = fields.Many2many('stock.production.lot',string="Lot",domain="[('product_id','=',product_id)]")
