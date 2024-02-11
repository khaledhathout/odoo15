# -*- coding: utf-8 -*-

from odoo import models, fields, api


class picking(models.Model):
    _inherit = 'stock.picking'

    vehicle_no = fields.Char("vehicle Number")
    driver_name = fields.Char("Driver Name")
    picking_ref = fields.Char("Picking Reference")
    location_well = fields.Char("Well Location")
    well_ref = fields.Char("Well Number")    
    purchase_date = fields.Datetime("Purchase Date", compute="_get_date_approve")

    def _get_date_approve(self):
        for rec in self:
            rec.purchase_date = False
            purchase = self.env['purchase.order'].search([('name', '=', rec.origin)], limit=1).date_order
            sale = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1).date_order
            if purchase:
                rec.purchase_date = purchase
            elif sale:
                rec.purchase_date = sale
            else:
                rec.purchase_date = False


class StockMove(models.Model):
    _inherit = 'stock.move'

    unit_qty = fields.Float(compute='_compute_unit_qty', string='Unit Qty')

    def _compute_unit_qty(self):
        for rec in self:
            width = rec.product_id.width
            length = rec.product_id.length
            height = rec.product_id.height

            rec.unit_qty = 0.0
            if rec.product_uom.equation == 'm2':
                rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or rec.product_qty == 0.0 else rec.product_qty / (
                        length * width)

            elif rec.product_uom.equation == 'm3':
                rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.product_qty == 0.0 else rec.product_qty / (
                        length * width * height)

            elif rec.product_uom.equation == 'lm':
                rec.unit_qty = 0.0 if length == 0.0 or rec.product_qty == 0.0 else rec.product_qty / length

            elif rec.product_uom.equation == 'qty' or not rec.product_uom.equation:
                rec.unit_qty = rec.product_qty