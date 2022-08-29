# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
import math
from datetime import datetime


class Planned_costs_final_goods(models.Model):
    _name = "planned.costs.final.goods"

    product_id = fields.Many2one('product.product', string="Product")
    material_costs = fields.Float('Material Costs')
    labour_costs = fields.Float('Labour Costs')
    overhead_costs = fields.Float('Overhead Costs')
    total_cost = fields.Float('Total Cost')
    product_unit_cost = fields.Float('Product Unit Cost (kg)')
    lot_id = fields.Many2one('stock.production.lot', string="Lot Id")
    production_id = fields.Many2one('mrp.production')
    margin = fields.Float('Margin')
    done_qty = fields.Float('Done')


class Actual_costs_final_goods(models.Model):
    _name = "actual.costs.final.goods"

    product_id = fields.Many2one('product.product', string="Product")
    material_costs = fields.Float('Material Costs')
    labour_costs = fields.Float('Labour Costs')
    overhead_costs = fields.Float('Overhead Costs')
    total_cost = fields.Float('Total Cost')
    product_unit_cost = fields.Float('Product Unit Cost')
    lot_id = fields.Many2one('stock.production.lot', string="Lot Id")
    production_id = fields.Many2one('mrp.production')
    margin = fields.Float('Margin')
    done_qty = fields.Float('Done')


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        self.write({'change_costing': self.change_costing + 1})
        return res

    actual_costing_ids = fields.One2many('actual.costs.final.goods', 'production_id', string="Actual Costing"
                                         , compute="_compute_actual_costing", store=True, copy=False
                                         )

    total_finished_kg = fields.Float(compute="_compute_total_finished_kg")
    planned_costing_ids = fields.One2many('planned.costs.final.goods', 'production_id', string="Planned Costing"
                                          , compute="_compute_planned_costing", store=True, copy=False
                                          )

    change_costing = fields.Float(string='Change Costing')

    def write(self, vals):

        if 'pro_overhead_cost_ids' in vals:
            vals.update({'change_costing': self.change_costing + 1})

        if 'finished_move_line_ids' in vals:
            vals.update({'change_costing': self.change_costing + 1})

        if 'total_finished_kg' in vals:
            vals.update({'change_costing': self.change_costing + 1})

        if 'pro_material_cost_ids' in vals:
            vals.update({'change_costing': self.change_costing + 1})

        if 'pro_labour_cost_ids' in vals:
            vals.update({'change_costing': self.change_costing + 1})

        if 'total_actual_all_cost' in vals:
            vals.update({'change_costing': self.change_costing + 1})

        res = super(MrpProduction, self).write(vals)
        return

    @api.depends('finished_move_line_ids', 'total_finished_kg', 'bom_id', 'change_costing')
    def _compute_planned_costing(self):

        for mrp in self:
            value = []
            margin = 0

            for un in mrp.planned_costing_ids:
                un.unlink()

            for line in mrp.finished_move_line_ids:
                material_costs = 0
                labour_costs = 0
                overhead_costs = 0
                total_cost = 0
                product_unit_cost = 0

                if line.product_uom_id.uom_type == 'reference':
                    if mrp.total_finished_kg > 0:
                        qty = 1
                        if mrp.bom_id.product_tmpl_id.id == line.product_id.product_tmpl_id.id:
                            qty = mrp.product_qty
                        else:
                            secondary_byproduct = self.env['mrp.subproduct.secondary'].search(
                                [('bom_id', '=', mrp.bom_id.id), ('product_id', '=', line.product_id.id)], limit=1)
                            if secondary_byproduct:
                                bom_unit_qty = secondary_byproduct.product_planned_qty / mrp.bom_id.product_qty
                                qty = bom_unit_qty * mrp.product_qty
                        material_costs = (line.qty_done / mrp.total_finished_kg) * mrp.total_material_cost
                        labour_costs = (line.qty_done / mrp.total_finished_kg) * mrp.total_labour_cost
                        overhead_costs = (line.qty_done / mrp.total_finished_kg) * mrp.total_overhead_cost
                        total_cost = (line.qty_done / mrp.total_finished_kg) * mrp.total_all_cost
                        product_unit_cost = total_cost / qty

                        vals = {'product_id': line.product_id.id,
                                'material_costs': material_costs,
                                'labour_costs': labour_costs,
                                'overhead_costs': overhead_costs,
                                'total_cost': total_cost,
                                'product_unit_cost': product_unit_cost,
                                'lot_id': line.lot_id.id,
                                'production_id': mrp.id,
                                'margin': margin,
                                'done_qty': line.qty_done}

                        value.append([0, 0, vals])

                if line.product_uom_id.uom_type == 'bigger':
                    if mrp.total_finished_kg > 0:
                        qty = line.qty_done * line.product_uom_id.factor_inv
                        qty_unit = 1

                        if mrp.bom_id.product_tmpl_id.id == line.product_id.product_tmpl_id.id:
                            qty_unit = mrp.product_qty * line.product_uom_id.factor_inv
                        else:
                            secondary_byproduct = self.env['mrp.subproduct.secondary'].search(
                                [('bom_id', '=', mrp.bom_id.id), ('product_id', '=', line.product_id.id)], limit=1)
                            if secondary_byproduct:
                                bom_unit_qty = secondary_byproduct.product_planned_qty / (
                                        mrp.bom_id.product_qty * line.product_uom_id.factor_inv)
                                qty_unit = bom_unit_qty * (mrp.product_qty * line.product_uom_id.factor_inv)

                        material_costs = (qty / mrp.total_finished_kg) * mrp.total_material_cost
                        labour_costs = (qty / mrp.total_finished_kg) * mrp.total_labour_cost
                        overhead_costs = (qty / mrp.total_finished_kg) * mrp.total_overhead_cost
                        total_cost = (qty / mrp.total_finished_kg) * mrp.total_all_cost
                        product_unit_cost = total_cost / qty_unit
                        vals = {'product_id': line.product_id.id,
                                'material_costs': material_costs,
                                'labour_costs': labour_costs,
                                'overhead_costs': overhead_costs,
                                'total_cost': total_cost,
                                'product_unit_cost': product_unit_cost,
                                'lot_id': line.lot_id.id,
                                'production_id': mrp.id,
                                'margin': margin,
                                'done_qty': line.qty_done}

                        value.append([0, 0, vals])

                if line.product_uom_id.uom_type == 'smaller':
                    if mrp.total_finished_kg > 0:
                        qty = line.qty_done / line.product_uom_id.factor
                        qty_unit = 1

                        if mrp.bom_id.product_tmpl_id.id == line.product_id.product_tmpl_id.id:
                            qty_unit = mrp.product_qty / line.product_uom_id.factor
                        else:
                            secondary_byproduct = self.env['mrp.subproduct.secondary'].search(
                                [('bom_id', '=', mrp.bom_id.id), ('product_id', '=', line.product_id.id)], limit=1)
                            if secondary_byproduct:
                                bom_unit_qty = secondary_byproduct.product_planned_qty / (
                                        mrp.bom_id.product_qty / line.product_uom_id.factor)
                                qty_unit = bom_unit_qty * (mrp.product_qty / line.product_uom_id.factor)

                        material_costs = (qty / mrp.total_finished_kg) * mrp.total_material_cost
                        labour_costs = (qty / mrp.total_finished_kg) * mrp.total_labour_cost
                        overhead_costs = (qty / mrp.total_finished_kg) * mrp.total_overhead_cost
                        total_cost = (qty / mrp.total_finished_kg) * mrp.total_all_cost
                        product_unit_cost = total_cost / qty_unit

                        vals = {'product_id': line.product_id.id,
                                'material_costs': material_costs,
                                'labour_costs': labour_costs,
                                'overhead_costs': overhead_costs,
                                'total_cost': total_cost,
                                'product_unit_cost': product_unit_cost,
                                'lot_id': line.lot_id.id,
                                'production_id': mrp.id,
                                'margin': margin,
                                'done_qty': line.qty_done}

                        value.append([0, 0, vals])

            if value:
                mrp.planned_costing_ids = value
            else:
                mrp.planned_costing_ids = value

        return

    def _compute_total_finished_kg(self):
        for line in self:
            total = 0
            for move in line.finished_move_line_ids:
                total = total + move.qty_done

            line.total_finished_kg = total

    @api.depends('change_costing', 'total_actual_all_cost')
    def _compute_actual_costing(self):

        for mrp in self:
            for un in mrp.actual_costing_ids:
                un.unlink()
            margin = 0
            flag = False
            value = False
            value = []

            for line in mrp.finished_move_line_ids:
                material_costs = 0
                labour_costs = 0
                overhead_costs = 0
                total_cost = 0
                product_unit_cost = 0

                if line.product_uom_id.uom_type == 'reference':
                    if mrp.total_finished_kg > 0:

                        material_costs = (line.qty_done / mrp.total_finished_kg) * mrp.total_actual_material_cost
                        labour_costs = (line.qty_done / mrp.total_finished_kg) * mrp.total_actual_labour_cost
                        overhead_costs = (line.qty_done / mrp.total_finished_kg) * mrp.total_actual_overhead_cost
                        total_cost = (line.qty_done / mrp.total_finished_kg) * mrp.total_actual_all_cost
                        if line.qty_done > 0:
                            product_unit_cost = total_cost / line.qty_done
                            vals = {'product_id': line.product_id.id,
                                    'material_costs': material_costs,
                                    'labour_costs': labour_costs,
                                    'overhead_costs': overhead_costs,
                                    'total_cost': total_cost,
                                    'product_unit_cost': product_unit_cost,
                                    'lot_id': line.lot_id.id,
                                    'production_id': mrp.id,
                                    'margin': margin,
                                    'done_qty': line.qty_done}

                            value.append([0, 0, vals])

                if line.product_uom_id.uom_type == 'bigger':
                    if mrp.total_finished_kg > 0:

                        qty = line.qty_done * line.product_uom_id.factor_inv
                        material_costs = (qty / mrp.total_finished_kg) * mrp.total_actual_material_cost
                        labour_costs = (qty / mrp.total_finished_kg) * mrp.total_actual_labour_cost
                        overhead_costs = (qty / mrp.total_finished_kg) * mrp.total_actual_overhead_cost
                        total_cost = (qty / mrp.total_finished_kg) * mrp.total_actual_all_cost
                        if qty > 0:
                            product_unit_cost = total_cost / qty

                            vals = {'product_id': line.product_id.id,
                                    'material_costs': material_costs,
                                    'labour_costs': labour_costs,
                                    'overhead_costs': overhead_costs,
                                    'total_cost': total_cost,
                                    'product_unit_cost': product_unit_cost,
                                    'lot_id': line.lot_id.id,
                                    'production_id': mrp.id,
                                    'margin': margin,
                                    'done_qty': line.qty_done}

                            value.append([0, 0, vals])

                if line.product_uom_id.uom_type == 'smaller':
                    if mrp.total_finished_kg > 0:

                        qty = line.qty_done / line.product_uom_id.factor
                        material_costs = (qty / mrp.total_finished_kg) * mrp.total_actual_material_cost
                        labour_costs = (qty / mrp.total_finished_kg) * mrp.total_actual_labour_cost
                        overhead_costs = (qty / mrp.total_finished_kg) * mrp.total_actual_overhead_cost
                        total_cost = (qty / mrp.total_finished_kg) * mrp.total_actual_all_cost
                        if qty > 0:
                            product_unit_cost = total_cost / qty

                            vals = {'product_id': line.product_id.id,
                                    'material_costs': material_costs,
                                    'labour_costs': labour_costs,
                                    'overhead_costs': overhead_costs,
                                    'total_cost': total_cost,
                                    'product_unit_cost': product_unit_cost,
                                    'lot_id': line.lot_id.id,
                                    'production_id': mrp.id,
                                    'margin': margin,
                                    'done_qty': line.qty_done}

                            value.append([0, 0, vals])

            if value:
                mrp.actual_costing_ids = value
            else:
                mrp.actual_costing_ids = value

        return
