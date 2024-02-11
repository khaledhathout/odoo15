# -*- coding: utf-8 -*-
from odoo.exceptions import UserError,ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT, float_round
from collections import defaultdict

from odoo import api, fields, models, _
import datetime
import math
import pytz
from odoo.tools import float_is_zero


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    equipment_cost_hour = fields.Float(
        string="Equipment Costs per hour", help="Specify cost of Equipments per hour.", default=0.0
    )


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _compute_total_cost(self):
        super(MrpBom, self)._compute_total_cost()
        self.bom_total_equipment_cost = sum([l.total_cost for l in self.bom_equipment_cost_ids])

    mo_auto_create = fields.Boolean()
    calendar_ids = fields.Many2many("resource.calendar")
    bom_equipment_cost_ids = fields.One2many(
        "mrp.bom.equipment.cost", "mrp_bom_equipment_id", "Equipment Cost"
    )
    bom_total_equipment_cost = fields.Float(
        compute='_compute_total_cost', string="Total Equipment Cost", default=0.0
    )

    @api.model
    def create(self, vals):
        res = super(MrpBom, self).create(vals)

        config = self.env['res.config.settings'].search([], order="id desc", limit=1)
        if res.operation_ids and config.process_costing == 'workcenter':
            for line in res.bom_equipment_cost_ids:
                line.unlink()

            for operation in res.operation_ids:
                value = {
                    'operation_id': operation.id,
                    'workcenter_id': operation.workcenter_id.id,
                    'cost': operation.workcenter_id.equipment_cost_hour or False,
                    'mrp_bom_equipment_id': res.id,

                }
                if operation.time_cycle > 0:
                    value.update({'planned_qty': operation.time_cycle / 60})
                res.write({'bom_equipment_cost_ids': [(0, 0, value)]})
        return res

    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        config = self.env['res.config.settings'].search([], order="id desc", limit=1)

        if vals.get('operation_ids') and config.process_costing == 'workcenter':
            for line in self.bom_equipment_cost_ids:
                line.unlink()
            for operation in self.operation_ids:
                value = {
                    'operation_id': operation.id,
                    'workcenter_id': operation.workcenter_id.id,
                    'cost': operation.workcenter_id.equipment_cost_hour or False,
                    'mrp_bom_equipment_id': self.id,
                }
                if operation.time_cycle > 0:
                    value.update({'planned_qty': operation.time_cycle / 60})
                self.write({'bom_equipment_cost_ids': [(0, 0, value)]})

        return res


class MrpBomLabourCost(models.Model):
    _inherit = "mrp.bom.labour.cost"

    employee_id = fields.Many2one('hr.employee')

    @api.onchange('employee_id')
    def onchange_emp(self):
        if self.employee_id:
            self.cost = self.employee_id.timesheet_cost


class MrpBomEquipmentCost(models.Model):
    _name = "mrp.bom.equipment.cost"

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        res = {}
        if not self.equipment_id:
            return res
        self.cost = self.equipment_id.cost

    @api.onchange('planned_qty', 'cost')
    def onchange_equipment_planned_qty(self):
        for line in self:
            line.total_cost = line.planned_qty * line.cost
            line.total_actual_cost = line.actual_qty * line.cost

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = res_user_id.company_id.currency_id

    operation_id = fields.Many2one(
        'mrp.routing.workcenter', string="Operation"
    )
    equipment_id = fields.Many2one('maintenance.equipment')
    planned_qty = fields.Float(string="Planned Hour", default=0.0)
    actual_qty = fields.Float(string="Actual Hour", default=0.0)
    workcenter_id = fields.Many2one('mrp.workcenter', string="Workcenter")
    cost = fields.Float(string="Cost/Hour")
    total_cost = fields.Float(
        compute='onchange_equipment_planned_qty', string="Total Cost"
    )
    total_actual_cost = fields.Float(
        compute='onchange_equipment_planned_qty', string="Total Actual Cost"
    )
    mrp_bom_equipment_id = fields.Many2one("mrp.bom", "Mrp Bom Equipment")
    mrp_pro_equipment_id = fields.Many2one("mrp.production", "Mrp Production Equipment")
    mrp_wo_equipment_id = fields.Many2one("mrp.workorder", "Mrp Workorder Equipment")
    currency_id = fields.Many2one(
        "res.currency", compute='get_currency_id', string="Currency"
    )


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_finish(self):
        for line in self:
            actual_hour = line.duration / 60
            equipment = self.env['mrp.bom.equipment.cost'].search(
                [('mrp_pro_equipment_id', '=', line.production_id.id), ('operation_id', '=', line.operation_id.id)])

            if equipment:
                equipment.write({'actual_qty': actual_hour})
            else:
                for lo in line.production_id.pro_equipment_cost_ids:
                    lo.write({'actual_qty': actual_hour})

        return super(MrpWorkorder, self).button_finish()

    def _compute_total_cost(self):
        super(MrpWorkorder, self)._compute_total_cost()

        for order in self:
            equipment_total = 0.0
            equipment_actual_total = 0.0
            for line in order.wo_equipment_cost_ids:
                equipment_total += line.total_cost
                equipment_actual_total += line.total_actual_cost
            order.total_equipment_cost = equipment_total
            order.total_actual_equipment_cost = equipment_actual_total

    def _compute_total_all_cost(self):
        super(MrpWorkorder, self)._compute_total_all_cost()
        for line in self:
            line.total_all_cost += line.total_equipment_cost
            line.total_actual_all_cost += line.total_actual_equipment_cost

    wo_equipment_cost_ids = fields.One2many(
        "mrp.bom.equipment.cost", "mrp_wo_equipment_id", "Equipment Cost"
    )
    total_equipment_cost = fields.Float(
        compute='_compute_total_cost', string="Total Equipment Cost", default=0.0
    )
    total_actual_equipment_cost = fields.Float(
        compute='_compute_total_cost', string="Total Actual Equipment Cost", default=0.0
    )

    def record_production(self):
        for line in self.production_id.pro_equipment_cost_ids:
            if line.operation_id.id == self.operation_id.id:
                line.write({'actual_qty': self.actual_hour_wo})
        return super(MrpWorkorder, self).record_production()


class StockMove(models.Model):
    _inherit = 'stock.move'

    available_location_ids = fields.Many2many('stock.location', string='locations', compute='get_available_locations')
    source_stock_location_id = fields.Many2one('stock.location')
    consumed = fields.Boolean(string="consumed move")
    valuation_value = fields.Float(string="Valuation Value", compute="_get_valuation_value")

    def _get_valuation_value(self):
        for rec in self:
            rec.valuation_value = abs(sum(self.env['stock.valuation.layer'].search([('stock_move_id', '=', rec.id)], limit=1).mapped("value")))

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                   cost):
        self.ensure_one()
        move_lines = False

        if self.consumed:
            material_cost = cost
            extra_cost = 0
            # get product valuation layer
            mo_id = self.unbuild_id.mo_id
            svls = mo_id.action_view_stock_valuation_layers()
            mo_svl = self.env['stock.valuation.layer'].search(svls['domain'])
            mo_svl = mo_svl.filtered(lambda l: l.product_id == self.product_id)
            if mo_svl:
                mo_svl = mo_svl[0]
                extra_cost = mo_svl.direct_operation_cost + mo_svl.direct_equipment_cost + mo_svl.direct_labour_cost + mo_svl.direct_overhead_cost

                material_cost = mo_svl.value - extra_cost

                extra_cost = (extra_cost / mo_svl.quantity) * self.product_uom_qty
                material_cost = (material_cost / mo_svl.quantity) * self.product_uom_qty

            move_lines = self._prepare_account_move_line(qty, material_cost, credit_account_id, debit_account_id,
                                                         description)

            if extra_cost > 0:
                move_lines += self._prepare_account_move_line(qty, extra_cost, credit_account_id,
                                                              mo_svl.product_id.categ_id.manufacturing_cost_account_id.id or credit_account_id,
                                                              description)
            else:
                move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id,
                                                             description)

        else:
            svl = self.env['stock.valuation.layer'].search([('id', '=', svl_id)])
            extra_cost = svl.direct_operation_cost + svl.direct_equipment_cost + svl.direct_labour_cost + svl.direct_overhead_cost
            material_cost = cost - extra_cost

            if extra_cost > 0:
                move_lines = self._prepare_account_move_line(qty, material_cost, credit_account_id, debit_account_id,
                                                             description)
                move_lines += self._prepare_account_move_line(qty, extra_cost,
                                                              svl.product_id.categ_id.manufacturing_cost_account_id.id or credit_account_id,
                                                              debit_account_id, description)
            else:
                move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id,
                                                             description)

        date = self._context.get('force_period_date', fields.Date.context_today(self))

        return {
            'journal_id': journal_id,
            'line_ids': move_lines,
            'date': date,
            'ref': description,
            'stock_move_id': self.id,
            'stock_valuation_layer_ids': [(6, None, [svl_id])],
            'move_type': 'entry',
        }

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def get_available_locations(self):
        for rec in self:
            rec.available_location_ids = False
            quants = self.env['stock.quant'].search(
                [('product_id', '=', rec.product_id.id), ('location_id.usage', 'in', ['internal'])])

            quants = quants.filtered(lambda q: (q.product_uom_id._compute_quantity(
                q.available_quantity, rec.product_uom)) >= rec.product_uom_qty)

            ids = quants.mapped('location_id') if quants else []
            if ids:
                rec.available_location_ids = ids

    @api.onchange('source_stock_location_id')
    def onchange_source_stock_location_id(self):
        self.location_id = False
        self.location_id = self.source_stock_location_id.id

    @api.depends('product_id', 'product_qty', 'picking_type_id', 'reserved_availability', 'priority', 'state', 'product_uom_qty', 'location_id')
    def _compute_forecast_information(self):
        res = super(StockMove,self)._compute_forecast_information()
        if 'params' in self.env.context and 'model' in self.env.context['params'] and self.env.context['params']['model'] == 'mrp.production':
            qty = self.product_id.with_context(location=self.source_stock_location_id.id)._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'))
            for rec in self:
                if rec.product_id.id in qty and 'free_qty' in qty[rec.product_id.id]:
                    if rec.product_uom_qty > qty[rec.product_id.id]['free_qty'] :
                        rec.forecast_availability = 0
        return res
    
    """@api.onchange('product_id','product_uom_qty')
    def onchange_product_id_quantity_uom(self):        
        # get availalbe quant location
        if self.env.context.get('force_available_qty'):
            self.location_id = False
            ids = []
            quants= self.env['stock.quant'].search([('product_id','=',self.product_id.id)])
            quants = quants.filtered(lambda q: q.available_quantity >= self.product_uom_qty and q.location_id.usage in ('internal'))
            ids = quants.mapped('location_id.id') if quants else []
            return {'domain':{'location_id':[('id','in',ids)]}}"""


class ProductCategory(models.Model):
    _inherit = 'product.category'

    manufacturing_cost_account_id = fields.Many2one('account.account', string='Manufacturing Cost Account'
                                                    , company_dependent=True,
                                                    domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]",
                                                    check_company=True, )


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    date_from = fields.Date(string='From', default=fields.Date.today())
    date_to = fields.Date(string='To', default=fields.Date.today())

    @api.onchange('target_model', 'date_from', 'date_to')
    def _get_production_ids(self):
        for rec in self:
            if rec.target_model != 'manufacturing':
                rec.mrp_production_ids = False

            if rec.date_from and rec.date_to and rec.state == 'draft' and rec.target_model == 'manufacturing':
                rec.mrp_production_ids = False
                rec.mrp_production_ids = [
                    (6, 0, self.env['mrp.production'].search([('date_planned_start', '>=', rec.date_from),
                                                              ('date_planned_start', '<=', rec.date_to)]).mapped('id'))]


class MrpCostStructure(models.AbstractModel):
    _inherit = 'report.mrp_account_enterprise.mrp_cost_structure'

    def get_lines(self, productions):
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        res = []
        currency_table = self.env['res.currency']._get_query_currency_table(
            {'multi_company': True, 'date': {'date_to': fields.Date.today()}})
        for product in productions.mapped('product_id'):
            mos = productions.filtered(lambda m: m.product_id == product)
            total_cost = 0.0
            # variables to calc cost share (i.e. between products/byproducts) since MOs can have varying distributions
            total_cost_by_mo = defaultdict(float)
            component_cost_by_mo = defaultdict(float)
            equipment_cost_by_mo = defaultdict(float)
            labour_cost_by_mo = defaultdict(float)
            overhead_cost_by_mo = defaultdict(float)
            operation_cost_by_mo = defaultdict(float)

            # Get operations details + cost
            operations = []
            Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
            if Workorders:
                query_str = """SELECT
                                    wo.production_id,
                                    wo.id,
                                    op.id,
                                    wo.name,
                                    partner.name,
                                    sum(t.duration),
                                    CASE WHEN wo.costs_hour = 0.0 THEN wc.costs_hour ELSE wo.costs_hour END AS costs_hour,
                                    currency_table.rate
                                FROM mrp_workcenter_productivity t
                                LEFT JOIN mrp_workorder wo ON (wo.id = t.workorder_id)
                                LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id)
                                LEFT JOIN res_users u ON (t.user_id = u.id)
                                LEFT JOIN res_partner partner ON (u.partner_id = partner.id)
                                LEFT JOIN mrp_routing_workcenter op ON (wo.operation_id = op.id)
                                LEFT JOIN {currency_table} ON currency_table.company_id = t.company_id
                                WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                                GROUP BY wo.production_id, wo.id, op.id, wo.name, wc.costs_hour, partner.name, t.user_id, currency_table.rate
                                ORDER BY wo.name, partner.name
                            """.format(currency_table=currency_table, )
                self.env.cr.execute(query_str, (tuple(Workorders.ids),))
                for mo_id, dummy_wo_id, op_id, wo_name, user, duration, cost_hour, currency_rate in self.env.cr.fetchall():
                    cost = duration / 60.0 * cost_hour * currency_rate
                    total_cost_by_mo[mo_id] += cost
                    operation_cost_by_mo[mo_id] += cost
                    operations.append([user, op_id, wo_name, duration / 60.0, cost_hour * currency_rate])

            # Get the cost of raw material effectively used
            raw_material_moves = []
            query_str = """SELECT
                                sm.product_id,
                                mo.id,
                                abs(SUM(svl.quantity)),
                                abs(SUM(svl.value)),
                                currency_table.rate
                             FROM stock_move AS sm
                       INNER JOIN stock_valuation_layer AS svl ON svl.stock_move_id = sm.id
                       LEFT JOIN mrp_production AS mo on sm.raw_material_production_id = mo.id
                       LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
                            WHERE sm.raw_material_production_id in %s AND sm.state != 'cancel' AND sm.product_qty != 0 AND scrapped != 't'
                         GROUP BY sm.product_id, mo.id, currency_table.rate""".format(currency_table=currency_table, )
            self.env.cr.execute(query_str, (tuple(mos.ids),))
            for product_id, mo_id, qty, cost, currency_rate in self.env.cr.fetchall():
                cost *= currency_rate
                raw_material_moves.append({
                    'qty': qty,
                    'cost': cost,
                    'product_id': ProductProduct.browse(product_id),
                })
                total_cost_by_mo[mo_id] += cost
                component_cost_by_mo[mo_id] += cost
                total_cost += cost

            # Get the cost of equipment effectively used
            equipments = []
            query_str = """SELECT
                                ec.equipment_id,
                                mo.id,
                                abs(SUM(ec.actual_qty)),
                                abs(SUM(ec.cost)),
                                currency_table.rate
                             FROM mrp_bom_equipment_cost AS ec
                       LEFT JOIN mrp_production AS mo on ec.mrp_pro_equipment_id = mo.id
                       LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
                            WHERE ec.mrp_pro_equipment_id in %s AND ec.actual_qty != 0
                         GROUP BY ec.equipment_id, mo.id, currency_table.rate""".format(currency_table=currency_table, )
            self.env.cr.execute(query_str, (tuple(mos.ids),))
            for equipment_id, mo_id, qty, cost, currency_rate in self.env.cr.fetchall():
                cost = qty * cost * currency_rate
                equipments.append({
                    'qty': qty,
                    'cost': cost,
                    'equipment_id': self.env['maintenance.equipment'].browse(equipment_id),
                })
                total_cost_by_mo[mo_id] += cost
                equipment_cost_by_mo[mo_id] += cost
                # total_cost += cost

            # Get the cost of labour effectively used
            labours = []
            query_str = """SELECT
                                lc.employee_id,
                                mo.id,
                                abs(SUM(lc.actual_qty)),
                                abs(SUM(lc.cost)),
                                currency_table.rate
                             FROM mrp_bom_labour_cost AS lc
                       LEFT JOIN mrp_production AS mo on lc.mrp_pro_labour_id = mo.id
                       LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
                            WHERE lc.mrp_pro_labour_id in %s AND lc.actual_qty != 0
                         GROUP BY lc.employee_id, mo.id, currency_table.rate""".format(currency_table=currency_table, )
            self.env.cr.execute(query_str, (tuple(mos.ids),))
            for employee_id, mo_id, qty, cost, currency_rate in self.env.cr.fetchall():
                cost = qty * cost * currency_rate
                labours.append({
                    'qty': qty,
                    'cost': cost,
                    'employee_id': self.env['hr.employee'].browse(employee_id),
                })
                total_cost_by_mo[mo_id] += cost
                labour_cost_by_mo[mo_id] += cost
                # total_cost += cost

            # Get the cost of overhead effectively used
            overheads = []
            query_str = """SELECT
                                oc.operation_id,
                                mo.id,
                                abs(SUM(oc.actual_qty)),
                                abs(SUM(oc.cost)),
                                currency_table.rate
                             FROM mrp_bom_overhead_cost AS oc
                       LEFT JOIN mrp_production AS mo on oc.mrp_pro_overhead_id = mo.id
                       LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
                            WHERE oc.mrp_pro_overhead_id in %s AND oc.actual_qty != 0
                         GROUP BY oc.operation_id, mo.id, currency_table.rate""".format(currency_table=currency_table, )
            self.env.cr.execute(query_str, (tuple(mos.ids),))
            for overhead_id, mo_id, qty, cost, currency_rate in self.env.cr.fetchall():
                cost = qty * cost * currency_rate
                overheads.append({
                    'qty': qty,
                    'cost': cost,
                    'overhead_id': self.env['mrp.routing.workcenter'].browse(overhead_id),
                })
                total_cost_by_mo[mo_id] += cost
                overhead_cost_by_mo[mo_id] += cost
                # total_cost += cost

            # Get the cost of scrapped materials
            scraps = StockMove.search(
                [('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])

            # Get the byproducts and their total + avg per uom cost share amounts
            total_cost_by_product = defaultdict(float)
            qty_by_byproduct = defaultdict(float)
            qty_by_byproduct_w_costshare = defaultdict(float)
            component_cost_by_product = defaultdict(float)
            equipment_cost_by_product = defaultdict(float)
            labour_cost_by_product = defaultdict(float)
            overhead_cost_by_product = defaultdict(float)
            operation_cost_by_product = defaultdict(float)
            # tracking consistent uom usage across each byproduct when not using byproduct's product uom is too much of a pain
            # => calculate byproduct qtys/cost in same uom + cost shares (they are MO dependent)
            byproduct_moves = mos.move_byproduct_ids.filtered(lambda m: m.state != 'cancel')
            for move in byproduct_moves:
                qty_by_byproduct[move.product_id] += move.product_qty
                # byproducts w/o cost share shouldn't be included in cost breakdown
                if move.cost_share != 0:
                    qty_by_byproduct_w_costshare[move.product_id] += move.product_qty
                    cost_share = move.cost_share / 100
                    total_cost_by_product[move.product_id] += total_cost_by_mo[move.production_id.id] * cost_share
                    component_cost_by_product[move.product_id] += component_cost_by_mo[
                                                                      move.production_id.id] * cost_share
                    equipment_cost_by_product[move.product_id] += equipment_cost_by_mo[
                                                                      move.production_id.id] * cost_share
                    labour_cost_by_product[move.product_id] += labour_cost_by_mo[move.production_id.id] * cost_share
                    overhead_cost_by_product[move.product_id] += overhead_cost_by_mo[move.production_id.id] * cost_share
                    operation_cost_by_product[move.product_id] += operation_cost_by_mo[
                                                                      move.production_id.id] * cost_share

            # Get product qty and its relative total + avg per uom cost share amount
            uom = product.uom_id
            mo_qty = 0
            for m in mos:
                cost_share = float_round(1 - sum(m.move_finished_ids.mapped('cost_share')) / 100,
                                         precision_rounding=0.0001)
                total_cost_by_product[product] += total_cost_by_mo[m.id] * cost_share
                component_cost_by_product[product] += component_cost_by_mo[m.id] * cost_share
                equipment_cost_by_product[product] += equipment_cost_by_mo[m.id] * cost_share
                labour_cost_by_product[product] += labour_cost_by_mo[m.id] * cost_share
                overhead_cost_by_product[product] += overhead_cost_by_mo[m.id] * cost_share
                operation_cost_by_product[product] += operation_cost_by_mo[m.id] * cost_share
                qty = sum(
                    m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped(
                        'product_uom_qty'))
                if m.product_uom_id.id == uom.id:
                    mo_qty += qty
                else:
                    mo_qty += m.product_uom_id._compute_quantity(qty, uom)

            total_actual_cost = 0.0
            for row in productions:
                total_actual_cost = row.total_actual_all_cost - row.total_actual_material_cost

            res.append({
                'product': product,
                'mo_qty': mo_qty,
                'mo_uom': uom,
                'operations': operations,
                'currency': self.env.company.currency_id,
                'raw_material_moves': raw_material_moves,
                'total_cost': total_cost,
                'total_actual_cost': total_actual_cost or 0.0,
                'scraps': scraps,
                'mocount': len(mos),
                'byproduct_moves': byproduct_moves,
                'component_cost_by_product': component_cost_by_product,
                'equipment_cost_by_product': equipment_cost_by_product,
                'labour_cost_by_product': labour_cost_by_product,
                'overhead_cost_by_product': overhead_cost_by_product,
                'operation_cost_by_product': operation_cost_by_product,
                'qty_by_byproduct': qty_by_byproduct,
                'qty_by_byproduct_w_costshare': qty_by_byproduct_w_costshare,
                'total_cost_by_product': total_cost_by_product,
                'productions': productions
            })
        return res
