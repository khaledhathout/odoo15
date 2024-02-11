# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fsm_return = fields.Boolean(string="Return Service")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_return_ids = fields.One2many('sale.return', 'sale_order_id')

    @api.depends('order_line.qty_delivered', 'order_line.qty_returned')
    def _compute_return(self):
        for order in self:
            order.return_count = len(self.env['sale.return'].search([('sale_order_id', '=', order.id),
                                                                     ('state', '!=', 'cancel')]))
            flag = False
            for l in order.order_line.filtered(lambda l: l.product_id.detailed_type != 'service'):
                if l.qty_delivered > l.qty_returned:
                    flag = True
                    break
            order.can_return = flag

    can_return = fields.Boolean(compute='_compute_return', default=True, store=True)
    return_count = fields.Integer(compute='_compute_return')

    def action_view_return(self):
        return {
            'name': 'Sale Returns',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.return',
            'domain': [('sale_order_id', '=', self.id), ],
            'context': {'default_partner_id': self.partner_id.id, 'default_sale_order_id': self.id},
            'target': 'current'
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('return_line_ids', 'return_line_ids.state')
    def _qty_return(self):
        for line in self:
            return_line = self.env['sale.return.line'].search([('state', '!=', 'cancel'), ('sale_order_id', '=', line.id)])
            line.qty_returned = sum([rl.qty_return for rl in return_line])
            #if line.qty_returned > line.product_uom_qty:
            #    raise ValidationError(_("Returned quantity can not be greater than order quantity."))

    qty_returned = fields.Float(string='Returned', compute='_qty_return')
    return_line_ids = fields.One2many('sale.return.line', 'sale_order_id')
