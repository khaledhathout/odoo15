# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import json
from odoo.exceptions import UserError
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_done = fields.Boolean("Delivery Done", compute="check_delivery", default=False, copy=False)
    show_measure = fields.Boolean(string="Show Measures", related="company_id.show_measure")

    def check_delivery(self):
        self.delivery_done = False
        if self.picking_ids:
            if self.picking_ids[0].state == "done":
                self.delivery_done = True
            if all(
                    line.quantity_done == line.product_uom_qty
                    for line in self.picking_ids[0].move_ids_without_package
            ):
                if self.picking_ids[0].state == "assigned":
                    self.picking_ids[0].button_validate()
                    if self.picking_ids[0].state == "done":
                        self.delivery_done = True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    length = fields.Float(string="Length",compute='_get_dimensions', digits='Dimension Decimal', copy=False)
    width = fields.Float(string="Width", compute='_get_dimensions', digits='Dimension Decimal', copy=False)
    height = fields.Float(string="Height",compute='_get_dimensions', digits='Dimension Decimal', copy=False)

    line_processed = fields.Boolean("Line Processed", default=False, copy=False)
    lm = fields.Float("LM", compute='_get_m2_m3', store=True)
    m2 = fields.Float("M2", compute='_get_m2_m3', store=True)
    m3 = fields.Float("M3", compute='_get_m2_m3', store=True)

    unit_qty = fields.Float(string="Quantity Of Unit")

    @api.constrains('lot_id')
    def compare_lot_qty(self):
        for rec in self:
            if rec.lot_id:
                if rec.product_uom_qty > rec.lot_id.product_qty:
                    raise UserError(_('Quantity grater than selected lot quantity'))       

    @api.onchange('product_id','lot_id')
    def onchange_lot_product(self):
        self._get_dimensions()
        self.product_uom_qty = self.lot_id.product_qty
        self.onchange_uom_qty()

    @api.depends('product_id','lot_id')
    def _get_dimensions(self):
        for rec in self :
            product_length = rec.product_id.length if rec.product_id else 0.0
            product_width = rec.product_id.width if rec.product_id else 0.0
            product_height = rec.product_id.height if rec.product_id else 0.0

            rec.length = rec.lot_id.length if rec.lot_id else product_length
            rec.width = rec.lot_id.width if rec.lot_id else product_width
            rec.height = rec.lot_id.height if rec.lot_id else product_height

    @api.depends('length', 'width', 'height', 'product_uom_qty', 'price_unit')
    def _get_m2_m3(self):
        for rec in self:
            rec.lm = 0.0
            rec.m2 = 0.0
            rec.m3 = 0.0
            rec.lm = (rec.length * rec.product_uom_qty)
            rec.m2 = (rec.length * rec.width * rec.product_uom_qty)
            rec.m3 = (rec.length * rec.width * rec.height * rec.product_uom_qty)

    @api.onchange('product_uom_qty','product_uom')
    def onchange_uom_qty(self):
        if self.product_uom:
            if self.product_uom.equation=='qty':
                self.unit_qty = self.product_uom_qty

            if self.product_uom.equation == 'm2' :
                if self.length == 0.0 or self.width == 0.0 or self.product_uom_qty == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.product_uom_qty/(self.length * self.width)

            if self.product_uom.equation == 'm3' :
                if self.length == 0.0 or self.width == 0.0 or self.height==0 or self.product_uom_qty == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.product_uom_qty/(self.length * self.width * self.height)

            if self.product_uom.equation == 'lm' :
                if self.length == 0.0 or self.product_uom_qty == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.product_uom_qty/(self.length)

    @api.onchange('unit_qty','product_uom')
    def onchange_unit_qty(self):
        if self.product_uom:

            if self.product_uom.equation=='qty':
                self.product_uom_qty = self.unit_qty


            if self.product_uom.equation == 'm2' :
                if self.length == 0.0 or self.width == 0.0 or self.unit_qty == 0.0:
                    self.product_uom_qty = 0.0
                else:
                    
                    self.product_uom_qty = self.unit_qty*(self.length * self.width)

            if self.product_uom.equation == 'm3' :
                if self.length == 0.0 or self.width == 0.0 or self.height==0 or self.unit_qty == 0.0:
                    self.product_uom_qty = 0.0
                else:
                    self.product_uom_qty = self.unit_qty*(self.length * self.width * self.height)

            if self.product_uom.equation == 'lm' :
                if self.length == 0.0 or self.unit_qty == 0.0:
                    self.product_uom_qty = 0.0
                else:
                    self.product_uom_qty = self.unit_qty*(self.length)


    def action_process_line(self):
        if self.order_id.picking_ids:
            picking_under_process = self.env["stock.picking"].search(
                [("sale_id", "=", self.order_id.id)]
            )
            moves_to_do = self.env["stock.move"].search(
                [
                    ("picking_id", "=", picking_under_process[0].id),
                    ("product_id", "=", self.product_id.id),
                    ("quantity_done", "!=", self.product_uom_qty),
                ]
            )

            if moves_to_do:
                for move in moves_to_do:
                    if move.product_id.id == self.product_id.id:
                        if self.product_id.tracking != "none":
                            self.line_processed = True
                            return move.action_show_details()
                        else:
                            move.quantity_done = move.product_uom_qty
                            self.line_processed = True

    def get_invoice_state(self):
        for rec in self:
            invoice_state = ""
            if rec.invoice_lines:
                if rec.invoice_lines[0].move_id.payment_state == "not_paid":
                    invoice_state = "Not Paid"
                elif rec.invoice_lines[0].move_id.payment_state == "in_payment":
                    invoice_state = "In Payment"
                elif rec.invoice_lines[0].move_id.payment_state == "paid":
                    invoice_state = "Paid"
                elif rec.invoice_lines[0].move_id.payment_state == "partial":
                    invoice_state = "Partial Paid"
                elif rec.invoice_lines[0].move_id.payment_state == "reversed":
                    invoice_state = "Reversed"
                else:
                    invoice_state = "Invoicing App Legacy"
            return invoice_state


class Uom(models.Model):
    _inherit = "uom.uom"

    EQUATION = [
        ('m2', 'M2'),
        ('m3', 'M3'),
        ('lm', 'LM'),
        ('qty', 'QTY'),
    ]

    equation = fields.Selection(EQUATION, string='Equation')

class ResCompany(models.Model):
    _inherit = "res.company"

    show_measure = fields.Boolean(string="Show Measures", default=False)
