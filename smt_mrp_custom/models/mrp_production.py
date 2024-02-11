# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT, float_round
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime
import math
import pytz
from odoo.tools import float_is_zero
from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    calendar_id = fields.Many2one("resource.calendar")
    calendar_attendance_id = fields.Many2one("resource.calendar.attendance")
    shift_hours = fields.Float(compute='_compute_shift_hours')
    unbuild_count = fields.Float(compute='_compute_unbuild_count')
    pro_equipment_cost_ids = fields.One2many(
        "mrp.bom.equipment.cost", "mrp_pro_equipment_id", "Equipment Cost"
    )
    total_equipment_cost = fields.Float(
        compute='_compute_total_cost', string="Total Equipment Cost", default=0.0
    )
    total_actual_equipment_cost = fields.Float(
        compute='_compute_total_cost', string="Total Actual Equipment Cost", default=0.0
    )
    direct_operation_cost = fields.Float("Direct Operation Cost", compute="_get_operation_cost")
    approved = fields.Boolean(string="Approved", tracking=True)
    lot_line_ids = fields.One2many('lot.lines', 'production_id', string="Lots")
    have_entry = fields.Boolean(compute='_check_entries')
    production_mechanism = fields.Selection([('one_lot', 'One Lot'), ('multiple_lot', 'Multiple Lots')],
                                            string='Production Mechanism')
    
    def _check_entries(self):
        for rec in self:
            rec.have_entry = False
            move_ids = self.env['stock.move'].search([('reference', '=', rec.name)])
            if self.env['stock.valuation.layer'].search(
                    [('stock_move_id', 'in', move_ids.mapped("id")), ('account_move_id', '!=', False)]):
                rec.have_entry = True

    def action_get_journal_entry(self):
        # This function is action to view entries
        move_ids = self.env['stock.move'].search([('reference', '=', self.name)]).mapped("id")
        entries = self.env['stock.valuation.layer'].search([('stock_move_id', 'in', move_ids)]).mapped(
            "account_move_id.id")
        return {
            'name': '{}: Entries'.format(self.name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', entries)]
        }

    def to_close_approve(self):
        self.write({'approved': True})

    # Overwrite onchange method
    @api.onchange('location_src_id', 'move_raw_ids', 'bom_id')
    def _onchange_location(self):
        source_location = self.location_src_id

    def _get_operation_cost(self):
        cost = 0.0
        for rec in self:
            for workorder in rec.workorder_ids:
                cost += workorder.duration / 60.0 * workorder.workcenter_id.costs_hour
            rec.direct_operation_cost = cost

    @api.depends('calendar_attendance_id')
    def _compute_shift_hours(self):
        self.shift_hours = self.calendar_attendance_id.hour_to - self.calendar_attendance_id.hour_from

    @api.onchange('calendar_id')
    def _onchange_calendar_id(self):
        self.calendar_attendance_id = False

    @api.onchange('calendar_attendance_id')
    def _onchange_calendar_attendance_id(self):
        labour_list = []
        self.pro_labour_cost_ids.unlink()
        if self.calendar_attendance_id:
            employees = self.env['hr.employee'].search([('resource_calendar_id', '=', self.calendar_id.id)])
            for emp in employees:
                labour_list += [(0, 0,
                                 {'employee_id': emp.id,
                                  'planned_qty': self.shift_hours,
                                  'actual_qty': self.shift_hours,
                                  'cost': emp.timesheet_cost
                                  })]
        self.write({'pro_labour_cost_ids': labour_list})

    def copy(self, default=None):
        res = super(MrpProduction, self).copy(default)
        for line in res.pro_equipment_cost_ids:
            line.unlink()
        for equipment in self.pro_equipment_cost_ids:
            new_line = equipment.copy()
            new_line.write({'mrp_pro_equipment_id': res.id})
        return res

    @api.model
    def create(self, values):
        res = super(MrpProduction, self).create(values)
        res.pro_overhead_cost_ids.write({'planned_qty': res.shift_hours, 'actual_qty': res.shift_hours})
        for equipment in res.bom_id.bom_equipment_cost_ids:
            val = {'operation_id': equipment.operation_id.id,
                   'equipment_id': equipment.equipment_id.id,
                   'planned_qty': res.shift_hours,
                   'actual_qty': res.shift_hours,
                   'cost': equipment.cost or False,
                   'mrp_pro_equipment_id': res.id,

                   }
            self.env["mrp.bom.equipment.cost"].create(val)
        return res

    def _compute_total_cost(self):
        super(MrpProduction, self)._compute_total_cost()
        equipment_total = 0.0
        equipment_actual_total = 0.0

        for line in self.pro_equipment_cost_ids:
            equipment_total += line.total_cost
            equipment_actual_total += line.total_actual_cost

        self.total_equipment_cost = equipment_total
        self.total_actual_equipment_cost = equipment_actual_total

    def _compute_total_all_cost(self):
        super(MrpProduction, self)._compute_total_all_cost()
        self.total_all_cost += self.total_equipment_cost
        self.total_actual_all_cost += self.total_actual_equipment_cost + self.direct_operation_cost

    @api.model
    def _auto_create_mrp_production(self):
        # Called by a cron
        dayofweek = datetime.datetime.today().weekday()
        attendance = self.env['resource.calendar.attendance'].search([('dayofweek', '=', dayofweek)])
        bom = self.env['mrp.bom'].search(
            [('calendar_ids', 'in', attendance.calendar_id.ids), ('mo_auto_create', '=', True)])
        for b in bom:
            for a in attendance.filtered(lambda c: c.calendar_id in b.calendar_ids):

                hour_from = math.modf(a.hour_from)
                tz = pytz.timezone(self.env.context.get('tz', 'UTC'))
                planned_date = datetime.datetime.today().replace(
                    hour=int(hour_from[1]), minute=int(hour_from[0] * 60), second=0, microsecond=0)
                utc = pytz.timezone('UTC')
                utc.localize(datetime.datetime.now())
                delta = utc.localize(planned_date) - tz.localize(planned_date)

                mrp = self.create({
                    'product_id': b.product_tmpl_id.product_variant_id.id,
                    'product_uom_id': b.product_tmpl_id.uom_id.id,
                    'bom_id': b.id,
                    'calendar_id': a.calendar_id.id,
                    'calendar_attendance_id': a.id,
                    'date_planned_start': planned_date - delta,
                    'company_id': b.company_id.id,
                })
                mrp._onchange_bom_id()
                mrp._onchange_location()
                mrp._onchange_location_dest()
                mrp._onchange_move_finished()
                mrp._onchange_move_raw()
                mrp._onchange_workorder_ids()
                mrp._onchange_location()
                mrp._onchange_location_dest()
                mrp._onchange_calendar_attendance_id()

                for material in mrp.move_raw_ids:
                    product_id = self.env['product.template'].search(
                        [('id', '=', material.product_id.product_tmpl_id.id)])

                    bom_material = self.env['mrp.bom.material.cost'].search(
                        [('product_id', '=', product_id.id), ('mrp_bom_material_id', '=', mrp.bom_id.id)], limit=1)

                    if bom_material:
                        vals = {
                            'product_id': product_id.id,
                            'planned_qty': material.product_uom_qty,
                            'uom_id': material.product_id.uom_id.id,
                            'cost': bom_material.cost,
                            'operation_id': bom_material.operation_id.id,
                            'mrp_pro_material_id': mrp.id,
                        }
                        if mrp.product_qty <= 1:
                            self.env['mrp.bom.material.cost'].create(vals)

    # calc cost
    def _cal_price(self, consumed_moves):
        res = super(MrpProduction, self)._cal_price(consumed_moves)
        finished_move = self.move_finished_ids.filtered(
            lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:

            qty_done = finished_move.product_uom._compute_quantity(
                finished_move.quantity_done, finished_move.product_id.uom_id)

            total_cost = ((
                                  finished_move.production_id.total_actual_all_cost - finished_move.production_id.direct_operation_cost) - finished_move.production_id.total_actual_material_cost)

            byproduct_moves = self.move_byproduct_ids.filtered(
                lambda m: m.state not in ('done', 'cancel') and m.quantity_done > 0)
            byproduct_cost_share = 0
            for byproduct in byproduct_moves:
                if byproduct.cost_share == 0:
                    continue
                byproduct_cost_share += byproduct.cost_share

                if byproduct.product_id.cost_method in ('fifo', 'average'):
                    byproduct.price_unit += total_cost * byproduct.cost_share / 100 / byproduct.product_uom._compute_quantity(
                        byproduct.quantity_done, byproduct.product_id.uom_id)

            if finished_move.product_id.cost_method in ('fifo', 'average'):
                finished_move.price_unit += total_cost * float_round(1 - byproduct_cost_share / 100,
                                                                     precision_rounding=0.0001) / qty_done
        return res

    def action_draft(self):
        self.state = 'draft'

    def _compute_unbuild_count(self):
        for rec in self:
            rec.unbuild_count = self.env['mrp.unbuild'].search_count([('mo_id', '=', rec.id)])

    def action_get_unbuild_order(self):
        # This function is action to view unbuild orders
        unbuild_orders = self.env['mrp.unbuild'].search([('mo_id', '=', self.id)])
        return {
            'name': '{}: Unbuild Orders'.format(self.name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mrp.unbuild',
            'domain': [('mo_id', 'in', unbuild_orders.mapped('mo_id.id'))]
        }

    def action_generate_serial(self):
        self.ensure_one()
        if self.product_id.tracking == 'lot':
            name = self.env['ir.sequence'].next_by_code('stock.lot.serial')
            exist_lot = self.env['stock.production.lot'].search([
                ('product_id', '=', self.product_id.id),
                ('company_id', '=', self.company_id.id),
                ('name', '=', name),
            ], limit=1)
            if exist_lot:
                name = self.env['stock.production.lot']._get_next_serial(self.company_id, self.product_id)
        else:
            name = self.env['stock.production.lot']._get_next_serial(self.company_id, self.product_id) or self.env[
                'ir.sequence'].next_by_code('stock.lot.serial')
        if self._context.get('from_line'):
            lot_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name': name,
            })
            self.lot_producing_id = lot_id
            lot_line_id = self.env['lot.lines'].search([('id', '=', self._context.get('line_id'))])
            lot_line_id.lot_producing_id = lot_id
        else:
            self.lot_producing_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name': name,
            })
        if self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids:
            self.move_finished_ids.filtered(
                lambda m: m.product_id == self.product_id).move_line_ids.lot_id = self.lot_producing_id
        if self.product_id.tracking == 'serial':
            self._set_qty_producing()

    @api.constrains("lot_line_ids")
    def _check_lot_qty(self):
        if self.production_mechanism == "multiple_lot" and self.state != "draft":
            pass
            # if sum(self.lot_line_ids.mapped("product_qty")) != self.product_qty:
            #     raise ValidationError(_("Total quantity must be equal to {} {}.".format(self.product_qty, self.product_uom_id.name)))

    def _post_inventory(self, cancel_backorder=False):
        moves_to_do, moves_not_to_do = set(), set()
        for move in self.move_raw_ids:
            if move.state == 'done':
                moves_not_to_do.add(move.id)
            elif move.state != 'cancel':
                moves_to_do.add(move.id)
                if move.product_qty == 0.0 and move.quantity_done > 0:
                    move.product_uom_qty = move.quantity_done
        self.env['stock.move'].browse(moves_to_do)._action_done(cancel_backorder=cancel_backorder)
        moves_to_do = self.move_raw_ids.filtered(lambda x: x.state == 'done') - self.env['stock.move'].browse(moves_not_to_do)
        # Create a dict to avoid calling filtered inside for loops.
        moves_to_do_by_order = defaultdict(lambda: self.env['stock.move'], [
            (key, self.env['stock.move'].concat(*values))
            for key, values in tools_groupby(moves_to_do, key=lambda m: m.raw_material_production_id.id)
        ])
        for order in self:
            finish_moves = order.move_finished_ids.filtered(lambda m: m.product_id == order.product_id and m.state not in ('done', 'cancel'))
            # the finish move can already be completed by the workorder.
            if finish_moves and not finish_moves.quantity_done:
                if order.production_mechanism == 'multiple_lot':
                    finish_moves.with_context(is_finish=True,order=order)._set_quantity_done(float_round(order.qty_producing - order.qty_produced, precision_rounding=order.product_uom_id.rounding, rounding_method='HALF-UP'))
                else:
                    finish_moves._set_quantity_done(float_round(order.qty_producing - order.qty_produced, precision_rounding=order.product_uom_id.rounding, rounding_method='HALF-UP'))
                    finish_moves.move_line_ids.lot_id = order.lot_producing_id
            order._cal_price(moves_to_do_by_order[order.id])
        moves_to_finish = self.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_to_finish = moves_to_finish._action_done(cancel_backorder=cancel_backorder)
        self.action_assign()
        for order in self:
            consume_move_lines = moves_to_do_by_order[order.id].mapped('move_line_ids')
            order.move_finished_ids.move_line_ids.consume_line_ids = [(6, 0, consume_move_lines.ids)]
        return True

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        if self.production_mechanism == "multiple_lot" and len(self.lot_line_ids) <= 0:
            raise ValidationError(_("You must add at least one lot!"))
        return res


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    have_valuation = fields.Boolean(compute='_check_valuation_layer')
    have_entry = fields.Boolean(compute='_check_valuation_layer')

    def _check_valuation_layer(self):
        for rec in self:
            rec.have_valuation = False
            rec.have_entry = False
            move_ids = self.env['stock.move'].search([('reference', '=', rec.name)])
            if move_ids:
                rec.have_valuation = True
            if self.env['stock.valuation.layer'].search([('stock_move_id', 'in', move_ids.mapped("id")), ('account_move_id', '!=', False)]):
                rec.have_entry = True

    def action_get_unbuild_valuation(self):
        # This function is action to view unbuild orders valuation
        move_ids = self.env['stock.move'].search([('reference', '=', self.name)]).mapped("id")
        return {
            'name': '{}: Valuation Layers'.format(self.name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.valuation.layer',
            'domain': [('stock_move_id', 'in', move_ids)]
        }

    def action_get_journal_entry(self):
        # This function is action to view entries
        move_ids = self.env['stock.move'].search([('reference', '=', self.name)]).mapped("id")
        entries = self.env['stock.valuation.layer'].search([('stock_move_id', 'in', move_ids)]).mapped("account_move_id.id")
        return {
            'name': '{}: Entries'.format(self.name),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', entries)]
        }


class LotLines(models.Model):
    _name = "lot.lines"

    production_id = fields.Many2one('mrp.production', string="Production")
    product_id = fields.Many2one('product.product', related="production_id.product_id", string="Product")
    company_id = fields.Many2one('res.company', related="production_id.company_id", string="Company")
    state = fields.Selection(related="production_id.state", string="State")
    product_tracking = fields.Selection(related="production_id.product_tracking", string="Product Tracking")
    lot_producing_id = fields.Many2one(
        'stock.production.lot', string='Lot/Serial Number', copy=False,
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    product_qty = fields.Float(string="Quantity", digits='Product Unit of Measure')
    product_uom_id = fields.Many2one('uom.uom', related="production_id.product_uom_id", string="Product")
    unit_qty = fields.Float(string="Quantity Of Unit")

    @api.onchange('product_qty','lot_producing_id')
    def _compute_unit_qty(self):
        for rec in self:
            width = rec.lot_producing_id.width
            length = rec.lot_producing_id.length
            height = rec.lot_producing_id.height

            rec.unit_qty = 0.0
            if rec.product_uom_id.equation == 'm2':
                rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or rec.product_qty == 0.0 else rec.product_qty / (
                        length * width)
            elif rec.product_uom_id.equation == 'm3':
                rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.product_qty == 0.0 else rec.product_qty / (
                        length * width * height)
            elif rec.product_uom_id.equation == 'lm':
                rec.unit_qty = 0.0 if length == 0.0 or rec.product_qty == 0.0 else rec.product_qty / length
            elif rec.product_uom_id.equation == 'qty' or not rec.product_uom_id.equation:
                rec.unit_qty = rec.product_qty

    @api.onchange('unit_qty','lot_producing_id')
    def _compute_product_qty(self):
        for rec in self:
            width = rec.lot_producing_id.width
            length = rec.lot_producing_id.length
            height = rec.lot_producing_id.height

            rec.product_qty = 0.0
            if rec.product_uom_id.equation == 'm2':
                rec.product_qty = 0.0 if length == 0.0 or width == 0.0 or rec.unit_qty == 0.0 else rec.unit_qty * (
                        length * width)
            elif rec.product_uom_id.equation == 'm3':
                rec.product_qty = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.unit_qty == 0.0 else rec.unit_qty * (
                        length * width * height)
            elif rec.product_uom_id.equation == 'lm':
                rec.product_qty = 0.0 if length == 0.0 or rec.unit_qty == 0.0 else rec.unit_qty * length
            elif rec.product_uom_id.equation == 'qty' or not rec.product_uom_id.equation:
                rec.product_qty = rec.unit_qty

    def action_generate_serial_line(self):
        for rec in self:
            rec.production_id.with_context(from_line=True, line_id=rec.id).action_generate_serial()


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _set_quantity_done(self, qty):
        """
        Set the given quantity as quantity done on the move through the move lines. The method is
        able to handle move lines with a different UoM than the move (but honestly, this would be
        looking for trouble...).
        @param qty: quantity in the UoM of move.product_uom
        """
        if self._context.get('is_finish'):
            for r in self._context.get('order').lot_line_ids:
                existing_smls = self.move_line_ids
                self.move_line_ids = self._set_quantity_done_prepare_vals(r.product_qty, lot_id=r.lot_producing_id.id)
                (self.move_line_ids - existing_smls)._apply_putaway_strategy()
        else:
            existing_smls = self.move_line_ids
            self.move_line_ids = self._set_quantity_done_prepare_vals(qty)
            # `_set_quantity_done_prepare_vals` may return some commands to create new SMLs
            # These new SMLs need to be redirected thanks to putaway rules
            (self.move_line_ids - existing_smls)._apply_putaway_strategy()

    def _set_quantity_done_prepare_vals(self, qty, lot_id=False):
        res = []
        for ml in self.move_line_ids:
            ml_qty = ml.product_uom_qty - ml.qty_done
            if float_compare(ml_qty, 0, precision_rounding=ml.product_uom_id.rounding) <= 0:
                continue
            # Convert move line qty into move uom
            if ml.product_uom_id != self.product_uom:
                ml_qty = ml.product_uom_id._compute_quantity(ml_qty, self.product_uom, round=False)

            taken_qty = min(qty, ml_qty)
            # Convert taken qty into move line uom
            if ml.product_uom_id != self.product_uom:
                taken_qty = self.product_uom._compute_quantity(ml_qty, ml.product_uom_id, round=False)

            # Assign qty_done and explicitly round to make sure there is no inconsistency between
            # ml.qty_done and qty.
            taken_qty = float_round(taken_qty, precision_rounding=ml.product_uom_id.rounding)
            res.append((1, ml.id, {'qty_done': ml.qty_done + taken_qty}))
            if ml.product_uom_id != self.product_uom:
                taken_qty = ml.product_uom_id._compute_quantity(ml_qty, self.product_uom, round=False)
            qty -= taken_qty

            if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
                break

        for ml in self.move_line_ids:
            if float_is_zero(ml.product_uom_qty, precision_rounding=ml.product_uom_id.rounding) and float_is_zero(ml.qty_done, precision_rounding=ml.product_uom_id.rounding):
                res.append((2, ml.id))

        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            if self.product_id.tracking != 'serial':
                vals = self._prepare_move_line_vals(quantity=0)
                vals['qty_done'] = qty
                vals['lot_id'] = lot_id
                res.append((0, 0, vals))
            else:
                uom_qty = self.product_uom._compute_quantity(qty, self.product_id.uom_id)
                for i in range(0, int(uom_qty)):
                    vals = self._prepare_move_line_vals(quantity=0)
                    vals['qty_done'] = 1
                    vals['product_uom_id'] = self.product_id.uom_id.id
                    res.append((0, 0, vals))
        return res