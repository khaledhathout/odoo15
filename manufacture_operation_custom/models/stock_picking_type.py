# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

  
    workcenter_ids = fields.Many2many('mrp.workcenter', string='Workcenter',related="production_id.operation_id.workcenter_ids")
    workcenter_id = fields.Many2one(
        'mrp.workcenter', 'Work Center', required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'progress': [('readonly', True)]},
        group_expand='_read_group_workcenter_id', check_company=True)
    operation_id = fields.Many2one('mrp.routing.workcenter',store=True,related="production_id.operation_id", string='Workcenter')
    name = fields.Char('name',related='operation_id.name')

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    workcenter_ids = fields.Many2many('mrp.workcenter', string='Workcenters')
    operation_id = fields.Many2one('mrp.routing.workcenter', string='Operation')
    @api.model
    def _get_default_picking_type_id(self, company_id):
        if 'no_type_id' in self.env.context:
             return
        else :
            return self.env['stock.picking.type'].search([
                ('code', '=', 'mrp_operation'),
                ('warehouse_id.company_id', '=', company_id),
            ], limit=1).id
        
    @api.depends('picking_type_id')
    def _compute_locations(self):
        if 'no_type_id' in self.env.context:
            return
        for production in self:
            if not production.picking_type_id.default_location_src_id or not production.picking_type_id.default_location_dest_id:
                company_id = production.company_id.id if (production.company_id and production.company_id in self.env.companies) else self.env.company.id
                fallback_loc = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
            production.location_src_id = production.picking_type_id.default_location_src_id.id or fallback_loc.id
            production.location_dest_id = production.picking_type_id.default_location_dest_id.id or fallback_loc.id

    def action_confirm(self):
        res = super(MrpProduction,self).action_confirm()
        for rec in self.move_raw_ids :
            if 'params' in self.env.context and 'model' in self.env.context['params'] and self.env.context['params']['model'] == 'mrp.production':
                qty = rec.product_id.with_context(location=rec.source_stock_location_id.id)._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'))
                if rec.product_id.id in qty and 'free_qty' in qty[rec.product_id.id]:
                    if rec.product_uom_qty > qty[rec.product_id.id]['free_qty'] :
                        raise ValidationError (_('Product  - %s is out of quantity')%(rec.product_id.display_name))
        return res
class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    workcenter_ids = fields.Many2many('mrp.workcenter', string='Workcenter',readonly=False)
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation')
    default_location_src_id = fields.Many2one('stock.location', string='Source Location',readonly=False,related="picking_type_id.default_location_src_id")
    default_location_dest_id = fields.Many2one('stock.location', string='Destination Location',readonly=False,related="picking_type_id.default_location_dest_id")
    color = fields.Integer(string='')
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material',index=True, ondelete='cascade', required=False, check_company=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=False, check_company=True)
    company_id = fields.Many2one('res.company', 'Company',related=False,default=lambda self: self.env.company)
    tag_ids = fields.Many2one('mrp.workcenter.tag')
    

    @api.onchange('tag_ids')
    def _onchange_tag_ids(self):
        workcenter = self.env['mrp.workcenter'].search([('tag_ids','in',self.tag_ids.ids)])
        self.workcenter_ids = workcenter
    
    
    def action_open_mo(self):
           return {
            'name': 'MO',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'context': {
                'default_picking_type_id':self.picking_type_id.id,
                'default_company_id': self.env.company.id,
                'default_company_id': self.env.company.id,
                'default_operation_id': self.id,
                'no_type_id':True},
            'view_mode': 'form',
            'view_type': 'form',
            # 'target': 'new'
        }
        
    
    def action_open_mo_tree(self):
           return {
            'name': 'Manufacturing Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'domain': [('operation_id','=',self.id)],
            'view_mode': 'tree,form',
            # 'target': 'new'
        }
    

class BOM(models.Model):
    _inherit = 'mrp.bom'
        
    mrp_operation_ids = fields.Many2many('mrp.routing.workcenter', string='Operation')

    def _create_workorder(self):
        for production in self:
            if not production.bom_id or not production.product_id:
                continue
            workorders_values = []

            product_qty = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id)
            exploded_boms, dummy = production.bom_id.explode(production.product_id, product_qty / production.bom_id.product_qty, picking_type=production.bom_id.picking_type_id)

            for bom, bom_data in exploded_boms:
                # If the operations of the parent BoM and phantom BoM are the same, don't recreate work orders.
                if not (bom.mrp_operation_ids and (not bom_data['parent_line'] or bom_data['parent_line'].bom_id.mrp_operation_ids != bom.mrp_operation_ids)):
                    continue
                for operation in bom.mrp_operation_ids:
                    if operation._skip_operation_line(bom_data['product']):
                        continue
                    workorders_values += [{
                        'name': operation.name,
                        'production_id': production.id,
                        'workcenter_id': operation.workcenter_id.id,
                        'product_uom_id': production.product_uom_id.id,
                        'operation_id': operation.id,
                        'state': 'pending',
                    }]
            production.workorder_ids = [(5, 0)] + [(0, 0, value) for value in workorders_values]
            for workorder in production.workorder_ids:
                workorder.duration_expected = workorder._get_duration_expected()

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    workcenter_ids = fields.Many2many('mrp.workcenter', string='Workcenter')