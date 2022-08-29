# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class Custom_quality_check(models.Model):
    _name = 'custom.quality.check'
    _description="Custom_quality_check"
    
    product_id  = fields.Many2one('product.product',string="Product")
    quantity = fields.Float(string="Quantity")
    lot_id = fields.Many2one('stock.production.lot',string="Lot")
    workorder_id = fields.Many2one('mrp.workorder',string="Workorder")
    name = fields.Char(string="Name")
    custom_uom_id = fields.Many2one('uom.uom',string="UOM")




class MrpProduction(models.Model):
    _inherit = "mrp.production"

    secondary_product_id_ids = fields.One2many('finished.goods', 'secondary_mrp_id')

    def button_mark_done(self):
        
        res = super(MrpProduction,self).button_mark_done()
        producr_moves = self.move_finished_ids

        move_ids = []
        for move in producr_moves :
            if move.product_id.id == self.product_id.id :
                move_ids.append(move.id)

        for line in self.secondary_product_id_ids :
            move_val = {
                    'product_id' : line.product_id.id,
                    'product_uom_qty' : line.product_qty,
                    'name' : self.name,
                    'product_uom' : line.product_id.uom_id.id,
                    'location_id' : line.product_id.property_stock_production.id,
                    'location_dest_id' : self.location_dest_id.id,
                    'production_id' : self.id
            }
            stock_move = self.env['stock.move'].sudo().create(move_val)
            line_vals = {'product_id' :line.product_id.id,
                        'product_uom_id' :line.product_id.uom_id.id,
                        'qty_done' : line.product_qty,
                        'move_id' : stock_move.id,
                        'location_id': line.product_id.property_stock_production.id,
                        'location_dest_id': self.location_dest_id.id,
                        'lot_id' : line.lot_id.id ,
            }
            stock_move_line = self.env['stock.move.line'].sudo().create(line_vals)
            move_ids.append(stock_move.id)
            stock_move.sudo()._action_confirm()
        self.move_finished_ids = [(6,0,move_ids)]

        res = super(MrpProduction,self).button_mark_done()
       

        return res

    def action_confirm(self):

        res = super(MrpProduction,self).action_confirm()
        for production in self:
            if production.bom_id:
                for bom_second in production.bom_id.secondary_byproduct :
    
                    qty_second = 0
                    if production.bom_id.product_qty > 0 :
                        qty_second = bom_second.product_planned_qty / production.bom_id.product_qty

                    tracking = False
                    if bom_second.product_id.tracking != 'none' :
                        tracking = True
                    else :
                        tracking=False

                    value = {
                    'product_id' : bom_second.product_id.id,
                    'product_qty': qty_second,
                    'secondary_mrp_id' : production.id,
                    'uom_id': bom_second.product_id.uom_id.id,
                    'tracking': tracking,
                    }
                    secondary_product = self.env['finished.goods'].create(value)

        return res

        
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: