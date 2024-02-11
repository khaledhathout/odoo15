# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    show_measure = fields.Boolean(string="Show Measures", related="company_id.show_measure")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    length = fields.Float(string="Length", compute='_get_dimensions', digits='Dimension Decimal', copy=False)
    width = fields.Float(string="Width", compute='_get_dimensions', digits='Dimension Decimal', copy=False)
    height = fields.Float(string="Height", compute='_get_dimensions', digits='Dimension Decimal', copy=False)
    unit_qty = fields.Float(string="Quantity Of Unit")

    @api.depends('product_id')
    def _get_dimensions(self):
        for rec in self:
            product_length = rec.product_id.length if rec.product_id else 0.0
            product_width = rec.product_id.width if rec.product_id else 0.0
            product_height = rec.product_id.height if rec.product_id else 0.0

            rec.length = product_length
            rec.width = product_width
            rec.height = product_height

    lm = fields.Float("LM", compute='_get_m2_m3', store=True)
    m2 = fields.Float("M2", compute='_get_m2_m3', store=True)
    m3 = fields.Float("M3", compute='_get_m2_m3', store=True)

    @api.depends('length', 'width', 'height', 'product_qty', 'price_unit')
    def _get_m2_m3(self):
        for rec in self:
            rec.lm = 0.0
            rec.m2 = 0.0
            rec.m3 = 0.0
            rec.lm = (rec.length * rec.product_qty)
            rec.m2 = (rec.length * rec.width * rec.product_qty)
            rec.m3 = (rec.length * rec.width * rec.height * rec.product_qty)

    @api.onchange('product_qty', 'product_uom')
    def onchange_uom_qty(self):
        if self.product_uom:
            if self.product_uom.equation == 'qty':
                self.unit_qty = self.product_qty

            if self.product_uom.equation == 'm2':
                if self.length == 0.0 or self.width == 0.0 or self.product_qty == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.product_qty / (self.length * self.width)

            if self.product_uom.equation == 'm3':
                if self.length == 0.0 or self.width == 0.0 or self.height == 0 or self.product_qty == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.product_qty / (self.length * self.width * self.height)

            if self.product_uom.equation == 'lm':
                if self.length == 0.0 or self.product_qty == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.product_qty / (self.length)

    @api.onchange('unit_qty', 'product_uom')
    def onchange_unit_qty(self):
        if self.product_uom:

            if self.product_uom.equation == 'qty':
                self.product_qty = self.unit_qty

            if self.product_uom.equation == 'm2':
                if self.length == 0.0 or self.width == 0.0 or self.unit_qty == 0.0:
                    self.product_qty = 0.0
                else:

                    self.product_qty = self.unit_qty * (self.length * self.width)

            if self.product_uom.equation == 'm3':
                if self.length == 0.0 or self.width == 0.0 or self.height == 0 or self.unit_qty == 0.0:
                    self.product_qty = 0.0
                else:
                    self.product_qty = self.unit_qty * (self.length * self.width * self.height)

            if self.product_uom.equation == 'lm':
                if self.length == 0.0 or self.unit_qty == 0.0:
                    self.product_qty = 0.0
                else:
                    self.product_qty = self.unit_qty * (self.length)

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

    def get_invoice_discount(self):
        for rec in self:
            discount_amount = 0.0
            invoice_lines_discount = sum(self.env['account.move.line'].search([('purchase_line_id', '=', rec.id)]).mapped('discount'))
            discount_amount = (rec.price_subtotal * (invoice_lines_discount / 100))
            return discount_amount


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    show_measure = fields.Boolean(string="Show Measures", related="company_id.show_measure")


class StockMove(models.Model):
    _inherit = 'stock.move'

    length = fields.Float("Length", compute="_git_sale_move_dimension", digits='Dimension Decimal')
    width = fields.Float("Width", compute="_git_sale_move_dimension", digits='Dimension Decimal')
    height = fields.Float("Height", compute="_git_sale_move_dimension", digits='Dimension Decimal')
    lm = fields.Float("LM", compute='_get_m2_m3', store=True)
    m2 = fields.Float("M2", compute='_get_m2_m3', store=True)
    m3 = fields.Float("M3", compute='_get_m2_m3', store=True)

    @api.depends('move_line_ids')
    def _git_sale_move_dimension(self):
        for rec in self:
            if rec.product_id.tracking != "none" and rec.picking_code == 'outgoing':
                rec.length = 0.0
                rec.width = 0.0
                rec.height = 0.0

                rec.sale_line_id.length = 0.0
                rec.sale_line_id.width = 0.0
                rec.sale_line_id.height = 0.0
                if len(rec.move_line_ids) > 0:
                    lot = self.env['stock.production.lot'].search([('id', '=', rec.move_line_ids[0].lot_id.id)])
                    if lot:
                        rec.lm = 0.0
                        rec.m2 = 0.0
                        rec.m3 = 0.0

                        rec.length = lot.length
                        rec.width = lot.width
                        rec.height = lot.height

                        rec.sale_line_id.length = lot.length
                        rec.sale_line_id.width = lot.width
                        rec.sale_line_id.height = lot.height

                        rec.lm = rec.sale_line_id.lm if rec.sale_line_id else rec.purchase_line_id.lm
                        rec.m2 = (rec.length * rec.width)
                        rec.m3 = (rec.length * rec.width * rec.height)
            else:
                rec.lm = rec.sale_line_id.lm if rec.sale_line_id else rec.purchase_line_id.lm
                rec.length = rec.sale_line_id.length if rec.sale_line_id else rec.purchase_line_id.length
                rec.width = rec.sale_line_id.width if rec.sale_line_id else rec.purchase_line_id.width
                rec.height = rec.sale_line_id.height if rec.sale_line_id else rec.purchase_line_id.height

    @api.depends('lot_ids', 'length', 'width', 'height')
    def _get_m2_m3(self):
        for move in self:
            move.lm = 0.0
            move.m2 = 0.0
            move.m3 = 0.0
            move.lm = (
                move.length * move.product_uom_qty * move.sale_line_id.price_unit if move.sale_line_id else move.purchase_line_id.price_unit)
            move.m2 = (move.length * move.width)
            move.m3 = (move.length * move.width * move.height)

            lots = self.env['stock.production.lot'].search([('id', 'in', move.lot_ids.ids)])
            """for lot in lots:
                if move.picking_code == 'incoming':
                    lot.length = move.length
                    lot.width = move.width
                    lot.height = move.height
                    lot.lm = move.lm"""


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    length = fields.Float("Length", digits='Dimension Decimal')
    width = fields.Float("Width", digits='Dimension Decimal')
    height = fields.Float("Height", digits='Dimension Decimal')
    lm = fields.Float("LM", compute='_get_m2_m3', store=True)
    m2 = fields.Float("M2", compute='_get_m2_m3', store=True)
    m3 = fields.Float("M3", compute='_get_m2_m3', store=True)
    show_measure = fields.Boolean(string="Show Measures", related="company_id.show_measure")

    unit_qty = fields.Float(string="Quantity Of Unit")

    @api.onchange('lenght', 'width', 'height')
    def onchange_diminsions(self):
        self.onchange_unit_qty()
        self.onchange_uom_qty()

        if self.lot_id:
            self.lot_id.write({'length': self.length,
                               'width': self.width,
                               'height': self.height,
                               })

    @api.onchange('location_dest_id', 'lot_id')
    def onchange_product(self):
        self.width = self.product_id.width
        self.height = self.product_id.height
        self.length = self.product_id.length
        if self.lot_id:
            self.width = self.lot_id.width
            self.height = self.lot_id.height
            self.length = self.lot_id.length

    @api.onchange('unit_qty', 'product_uom_id')
    def onchange_unit_qty(self):
        if self.product_uom_id:
            if self.product_uom_id.equation == 'qty':
                self.qty_done = self.unit_qty

            if self.product_uom_id.equation == 'm2':
                if self.length == 0.0 or self.width == 0.0 or self.unit_qty == 0.0:
                    self.qty_done = 0.0
                else:

                    self.qty_done = self.unit_qty * (self.length * self.width)

            if self.product_uom_id.equation == 'm3':
                if self.length == 0.0 or self.width == 0.0 or self.height == 0 or self.unit_qty == 0.0:
                    self.qty_done = 0.0
                else:
                    self.qty_done = self.unit_qty * (self.length * self.width * self.height)

            if self.product_uom_id.equation == 'lm':
                if self.length == 0.0 or self.unit_qty == 0.0:
                    self.qty_done = 0.0
                else:
                    self.qty_done = self.unit_qty * (self.length)

    @api.onchange('qty_done', 'product_uom_id')
    def onchange_uom_qty(self):
        if self.product_uom_id:

            if self.product_uom_id.equation == 'qty':
                self.unit_qty = self.qty_done

            if self.product_uom_id.equation == 'm2':
                if self.length == 0.0 or self.width == 0.0 or self.qty_done == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.qty_done / (self.length * self.width)

            if self.product_uom_id.equation == 'm3':
                if self.length == 0.0 or self.width == 0.0 or self.height == 0 or self.qty_done == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.qty_done / (self.length * self.width * self.height)

            if self.product_uom_id.equation == 'lm':
                if self.length == 0.0 or self.qty_done == 0.0:
                    self.unit_qty = 0.0
                else:
                    self.unit_qty = self.qty_done / (self.length)

    @api.depends('lot_id')
    def _get_m2_m3(self):
        for rec in self:
            lot = self.env['stock.production.lot'].search([('id', '=', rec.lot_id.id)], limit=1)
            if lot:
                rec.lm = 0.0
                rec.m2 = 0.0
                rec.m3 = 0.0

                # rec.length = lot.length
                # rec.width = lot.width
                # rec.height = lot.height
                rec.lm = lot.lm

                rec.m2 = (rec.length * rec.width)
                rec.m3 = (rec.length * rec.width * rec.height)

    def _assign_production_lot(self, lot):
        for rec in self :
            rec.write({'lot_id': lot.id})
            lot.write({'length': rec.length,
                    'width': rec.width,
                    'height': rec.height,
                    })


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    length = fields.Float("Length", digits='Dimension Decimal')
    width = fields.Float("Width", digits='Dimension Decimal')
    height = fields.Float("Height", digits='Dimension Decimal')
    lm = fields.Float("LM")
    m2 = fields.Float("M2", compute='_get_m2_m3', store=True)
    m3 = fields.Float("M3", compute='_get_m2_m3', store=True)
    show_measure = fields.Boolean(string="Show Measures", related="company_id.show_measure")
    product_qty_units = fields.Float(compute='_compute_product_qty_units', string='Quantity (Units)')

    def _compute_product_qty_units(self):
        for rec in self:
            width = rec.width
            length = rec.length
            height = rec.height

            rec.product_qty_units = 0.0
            if rec.product_id.uom_id.equation == 'm2':
                rec.product_qty_units = 0.0 if length == 0.0 or width == 0.0 or rec.product_qty == 0.0 else rec.product_qty / (
                        length * width)
            elif rec.product_id.uom_id.equation == 'm3':
                rec.product_qty_units = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.product_qty == 0.0 else rec.product_qty / (
                            length * width * height)
            elif rec.product_id.uom_id.equation == 'lm':
                rec.product_qty_units = 0.0 if length == 0.0 or rec.product_qty == 0.0 else rec.product_qty / length
            elif rec.product_id.uom_id.equation == 'qty' or not rec.product_id.uom_id.equation:
                rec.product_qty_units = rec.product_qty

    @api.depends('length', 'width', 'height')
    def _get_m2_m3(self):
        for rec in self:
            rec.m2 = 0.0
            rec.m3 = 0.0
            rec.m2 = (rec.length * rec.width)
            rec.m3 = (rec.length * rec.width * rec.height)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    length = fields.Float("Length", digits='Dimension Decimal')
    width = fields.Float("Width", digits='Dimension Decimal')
    height = fields.Float("Height", digits='Dimension Decimal')
    ml = fields.Float("LM", compute='_get_m2_m3', store=True)
    m2 = fields.Float("M2", compute='_get_m2_m3', store=True)
    m3 = fields.Float("M3", compute='_get_m2_m3', store=True)
    show_measure = fields.Boolean(string="Show Measures", related="company_id.show_measure")
    unit_qty = fields.Float(string="Quantity Of Unit")
    # product_qty = fields.Float(compute='_compute_product_qty')

    @api.onchange('product_id')
    def _get_dimensions(self):
        for rec in self:
            product_length = rec.product_id.length if rec.product_id else 0.0
            product_width = rec.product_id.width if rec.product_id else 0.0
            product_height = rec.product_id.height if rec.product_id else 0.0

            rec.length = product_length
            rec.width = product_width
            rec.height = product_height

    @api.onchange('product_qty', 'product_uom_id', 'length', 'width', 'height', 'lot_line_ids')
    def _compute_unit_qty(self):
        for rec in self:
            if rec.production_mechanism == 'one_lot':
                width = rec.width
                length = rec.length
                height = rec.height
                rec.unit_qty = 0.0
                if rec.product_uom_id.equation == 'm2':
                    rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or rec.product_qty == 0.0 else rec.product_qty / (length * width)
                elif rec.product_uom_id.equation == 'm3':
                    rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.product_qty == 0.0 else rec.product_qty / (length * width * height)
                elif rec.product_uom_id.equation == 'lm':
                    rec.unit_qty = 0.0 if length == 0.0 or rec.product_qty == 0.0 else rec.product_qty / length
                elif rec.product_uom_id.equation == 'qty' or not rec.product_uom_id.equation:
                    rec.unit_qty = rec.product_qty

            if rec.production_mechanism == 'multiple_lot':
                unit_qty = 0
                if rec.lot_line_ids:
                    for lot in rec.lot_line_ids:
                        if lot.lot_producing_id and lot.product_qty != 0.0: 
                            unit_qty+= lot.unit_qty
                rec.unit_qty = unit_qty if unit_qty != 0 else rec.unit_qty

    @api.onchange('unit_qty', 'product_uom_id', 'length', 'width', 'height', 'lot_line_ids')
    def _compute_product_qty(self):
        for rec in self:
            if rec.production_mechanism == 'one_lot':
                width = rec.width
                length = rec.length
                height = rec.height
                rec.product_qty = 0.0
                if rec.product_uom_id.equation == 'm2':
                    rec.product_qty = 0.0 if length == 0.0 or width == 0.0 or rec.unit_qty == 0.0 else rec.unit_qty * (length * width)
                elif rec.product_uom_id.equation == 'm3':
                    rec.product_qty = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.unit_qty == 0.0 else rec.unit_qty * (length * width * height)
                elif rec.product_uom_id.equation == 'lm':
                    rec.product_qty = 0.0 if length == 0.0 or rec.unit_qty == 0.0 else rec.unit_qty * length
                elif rec.product_uom_id.equation == 'qty' or not rec.product_uom_id.equation:
                    rec.product_qty = rec.unit_qty

            if rec.production_mechanism == 'multiple_lot':
                product_qty = 0
                if rec.lot_line_ids:
                    for lot in rec.lot_line_ids:
                        if lot.lot_producing_id and lot.product_qty != 0.0: 
                            product_qty+= lot.product_qty
                rec.product_qty = product_qty if product_qty != 0 else rec.product_qty

    def action_generate_serial(self):
        res = super(MrpProduction, self).action_generate_serial()
        self.ensure_one()

        lot = self.move_raw_ids.move_line_ids.filtered(lambda l: l.lot_id)
        if lot:
            lot = lot.mapped('lot_id.name')
            self.lot_producing_id.write({'name': lot[0] + '/' + self.lot_producing_id.name})

    @api.depends('lot_producing_id', 'length', 'width', 'height', 'product_qty')
    def _get_m2_m3(self):
        for production in self:
            production.m2 = 0.0
            production.m3 = 0.0
            production.ml = 0.0

            production.ml = production.length * production.unit_qty
            production.m2 = (production.length * production.width) * production.unit_qty
            production.m3 = (production.length * production.width * production.height) * production.unit_qty

            lot = self.env['stock.production.lot'].search([('id', '=', production.lot_producing_id.id)])
            if lot:
                lot.length = production.length
                lot.width = production.width
                lot.height = production.height
