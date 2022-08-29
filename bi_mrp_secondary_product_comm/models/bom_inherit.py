# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models,api
from odoo.addons import decimal_precision as dp
from odoo.tools import float_round

class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    
    def _compute_bom_total_planned_cost(self):
        total = 0.0
        for rec in self:
            for line in rec.secondary_byproduct:
                total += line.total_planned_cost
            rec.total_bom_secondary_byproduct_cost = total 
    
    secondary_byproduct = fields.One2many('mrp.subproduct.secondary', 'bom_id', 'Secondary', copy=True)
    total_bom_secondary_byproduct_cost = fields.Float(compute='_compute_bom_total_planned_cost',string='Total Secondary Product Cost')
    

class MrpSubProduct(models.Model):
    _name = 'mrp.subproduct.secondary'
    
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_planned_qty = fields.Float('Product Planned Qty', default=1.0)
    product_actual_qty = fields.Float('Product Actual Qty', default=1.0)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    bom_id = fields.Many2one('mrp.bom', 'BoM', ondelete='cascade')
    mrp_id = fields.Many2one('mrp.production', 'MRP', ondelete='cascade')
    cost = fields.Float('Product Secondary Cost',default=0.0)
    total_planned_cost = fields.Float(string='Total Planned Cost')
    total_actual_cost = fields.Float(string='Total Actual Cost')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: