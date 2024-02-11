# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT, float_round
from collections import defaultdict

from odoo import api, fields, models, _
import datetime
import math
import pytz
from odoo.tools import float_is_zero

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    direct_equipment_cost = fields.Float("Direct Actual Equipment Cost", compute="_get_cost")
    direct_labour_cost = fields.Float("Direct Actual Labour Cost", compute="_get_cost")
    direct_overhead_cost = fields.Float("Direct Actual Overhead Cost", compute="_get_cost")
    direct_material_cost = fields.Float("Direct Material Cost", compute="_get_cost")
    direct_operation_cost = fields.Float("Direct Operation Cost", compute="_get_cost")

    def _get_cost(self):
        for rec in self:
            # inital value
            equipment_cost = 0.0
            labour_cost = 0.0
            overhead_cost = 0.0
            material_cost = 0.0
            operation_cost = 0.0

            # cost from production

            equipment_cost = rec.stock_move_id.production_id.total_actual_equipment_cost
            labour_cost = rec.stock_move_id.production_id.total_actual_labour_cost
            overhead_cost = rec.stock_move_id.production_id.total_actual_overhead_cost
            material_cost = rec.stock_move_id.production_id.total_actual_material_cost

            # calculate operation cost
            for workorder in rec.stock_move_id.production_id.workorder_ids:
                operation_cost += workorder.duration / 60.0 * workorder.workcenter_id.costs_hour

            # get byproduct cost share
            byproduct_moves = rec.stock_move_id.production_id.move_byproduct_ids.filtered(lambda m: m.state != 'cancel' and m.quantity_done > 0)

            cost_share = sum(move.cost_share for move in byproduct_moves)

            if cost_share > 0.0:
                cost_share = cost_share / 100

                material_cost = material_cost - (material_cost * cost_share)
                equipment_cost = equipment_cost - (equipment_cost * cost_share)
                labour_cost = labour_cost - (labour_cost * cost_share)
                overhead_cost = overhead_cost - (overhead_cost * cost_share)
                operation_cost = operation_cost - (operation_cost * cost_share)

                for by_product in rec.stock_move_id.production_id.move_byproduct_ids:
                    if by_product.product_id == rec.product_id:
                        op_cost = 0.0
                        material_cost = rec.stock_move_id.production_id.total_actual_material_cost * (by_product.cost_share / 100)
                        equipment_cost = rec.stock_move_id.production_id.total_actual_equipment_cost * (by_product.cost_share / 100)
                        labour_cost = rec.stock_move_id.production_id.total_actual_labour_cost * (by_product.cost_share / 100)
                        overhead_cost = rec.stock_move_id.production_id.total_actual_overhead_cost * (by_product.cost_share / 100)
                        for workorder in rec.stock_move_id.production_id.workorder_ids:
                            op_cost += workorder.duration / 60.0 * workorder.workcenter_id.costs_hour
                        operation_cost = op_cost * (by_product.cost_share / 100)


            rec.direct_material_cost = material_cost
            rec.direct_equipment_cost = equipment_cost
            rec.direct_labour_cost = labour_cost
            rec.direct_overhead_cost = overhead_cost
            rec.direct_operation_cost = operation_cost


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def _generate_move_from_existing_move(self, move, factor, location_id, location_dest_id):
        res = super(MrpUnbuild,self)._generate_move_from_existing_move(move, factor, location_id, location_dest_id)
        res.write({'consumed':True})
        return res