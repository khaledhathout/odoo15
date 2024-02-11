# Copyright 2020 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009

from collections import defaultdict

from odoo import api, fields, models, _
import math


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    on_hand_units = fields.Float(compute='_compute_avialable_unit', string='Onhand QTY (Units)')
    counted_units = fields.Float(string='Counted QTY (Units)')
    difference_units = fields.Float(compute='_compute_avialable_unit', string='Difference (Units)')
    length = fields.Float(string="Length", digits='Dimension Decimal')
    width = fields.Float(string="Width", digits='Dimension Decimal')
    height = fields.Float(string="Height", digits='Dimension Decimal')

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_write()
        res += ['counted_units']
        return res

    def _compute_avialable_unit(self):
        for rec in self:
            width = rec.lot_id.width if rec.lot_id else rec.product_id.width
            length = rec.lot_id.length if rec.lot_id else rec.product_id.length
            height = rec.lot_id.height if rec.lot_id else rec.product_id.height

            rec.on_hand_units = 0.0
            rec.difference_units = 0.0
            if rec.product_id.uom_id.equation == 'm2':
                rec.on_hand_units = 0.0 if length == 0.0 or width == 0.0 or rec.quantity == 0.0 else rec.quantity / (
                        length * width)
                rec.difference_units = 0.0 if length == 0.0 or width == 0.0 or rec.inventory_diff_quantity == 0.0 else rec.inventory_diff_quantity / (
                        length * width)

            elif rec.product_id.uom_id.equation == 'm3':
                rec.on_hand_units = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.quantity == 0.0 else rec.quantity / (
                        length * width * height)

                rec.difference_units = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.inventory_diff_quantity == 0.0 else rec.inventory_diff_quantity / (
                        length * width * height)

            elif rec.product_id.uom_id.equation == 'lm':
                rec.on_hand_units = 0.0 if length == 0.0 or rec.quantity == 0.0 else rec.quantity / length
                rec.difference_units = 0.0 if length == 0.0 or rec.inventory_diff_quantity == 0.0 else rec.inventory_diff_quantity / length

            elif rec.product_id.uom_id.equation == 'qty' or not rec.product_id.uom_id.equation:
                rec.on_hand_units = rec.quantity
                rec.difference_units = rec.inventory_diff_quantity

    @api.onchange('inventory_quantity')
    def _compute_counted_units(self):
        for rec in self:
            width = rec.lot_id.width if rec.lot_id else rec.product_id.width
            length = rec.lot_id.length if rec.lot_id else rec.product_id.length
            height = rec.lot_id.height if rec.lot_id else rec.product_id.height

            rec.counted_units = 0.0
            if rec.product_id.uom_id.equation == 'm2':
                rec.counted_units = 0.0 if length == 0.0 or width == 0.0 or rec.inventory_quantity == 0.0 else rec.inventory_quantity / (
                        length * width)

            elif rec.product_id.uom_id.equation == 'm3':
                rec.counted_units = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.inventory_quantity == 0.0 else rec.inventory_quantity / (
                        length * width * height)

            elif rec.product_id.uom_id.equation == 'lm':
                rec.counted_units = 0.0 if length == 0.0 or rec.inventory_quantity == 0.0 else rec.inventory_quantity / length

            elif rec.product_id.uom_id.equation == 'qty' or not rec.product_id.uom_id.equation:
                rec.counted_units = rec.inventory_quantity

    @api.onchange('counted_units')
    def _compute_inventory_quantity(self):
        for rec in self:
            width = rec.lot_id.width if rec.lot_id else rec.product_id.width
            length = rec.lot_id.length if rec.lot_id else rec.product_id.length
            height = rec.lot_id.height if rec.lot_id else rec.product_id.height

            rec.inventory_quantity = 0.0
            if rec.product_id.uom_id.equation == 'm2':
                rec.inventory_quantity = 0.0 if length == 0.0 or width == 0.0 or rec.counted_units == 0.0 else rec.counted_units * (
                        length * width)

            elif rec.product_id.uom_id.equation == 'm3':
                rec.inventory_quantity = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.counted_units == 0.0 else rec.counted_units * (
                        length * width * height)

            elif rec.product_id.uom_id.equation == 'lm':
                rec.inventory_quantity = 0.0 if length == 0.0 or rec.counted_units == 0.0 else rec.counted_units * length

            elif rec.product_id.uom_id.equation == 'qty' or not rec.product_id.uom_id.equation:
                rec.inventory_quantity = rec.counted_units
