from odoo import models, fields, api, _
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_new_mo = fields.Boolean()


    def action_confirm(self):
        if not self.bom_id and self.is_new_mo:
            raise ValidationError(_('Please add valid bill of material first..! '))
        res = super(MrpProduction,self).action_confirm()
        return res

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):

        for rec in self.order_line:
            if not rec.bom_id:
                raise ValidationError(("Please add Bill of Material in sale order line!!"))
            if rec.bom_id and rec.product_id:
                if rec.bom_id.product_tmpl_id != rec.product_id.product_tmpl_id:
                     raise ValidationError(("Sale Order Product and Bill of Material's Product must be same!!!"))

            mo=self.env['mrp.production'].create({
                            'product_id': rec.bom_id.product_id.id or rec.product_id.id,
                            'product_qty':rec.bom_id.product_qty,
                            'product_uom_qty':rec.bom_id.product_qty,
                            'product_uom_id': rec.product_uom.id,
                            'origin':self.name,
                            'is_new_mo':True,
                            })
            mo._onchange_move_raw()

        return super(SaleOrder,self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bom_id = fields.Many2one("mrp.bom",string="Bill of Material")


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.constrains('product_id', 'product_tmpl_id', 'bom_line_ids')
    def _check_product_recursion(self):

        for bom in self:
            if bom.product_id and bom.bom_line_ids:
                if bom.bom_line_ids.filtered(lambda x: x.product_id == bom.product_id):
                    raise ValidationError(_('BOM line product %s should not be same as BOM product.') % bom.display_name)
            if bom.product_tmpl_id and bom.bom_line_ids:
                if bom.bom_line_ids.filtered(lambda x: x.product_id.product_tmpl_id == bom.product_tmpl_id):
                    raise ValidationError(_('BOM line product %s should not be same as BOM product.') % bom.display_name)

 