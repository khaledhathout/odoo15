# Copyright 2020 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('pricelist_id')
    def onchange_pricelist_so_lines(self):
        # Recalculate so lines when change pricelist
        for line in self.order_line:
            line.product_id_change()

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        # Inherit this function to calculate price for so template lines 
        # based on selected pricelist
        super(SaleOrder, self).onchange_sale_order_template_id()
        self.onchange_pricelist_so_lines()
        self.update_uom()

    def update_uom(self):
        if self.sale_order_template_id:
            for line in self.order_line:
                template_product = self.env['sale.order.template.line'].search(
                    [('sale_order_template_id', '=', self.sale_order_template_id.id),
                     ('product_id', '=', line.product_id.id)], limit=1)
                line.update({'product_uom': template_product.product_uom_id.id})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    forein_currency_id = fields.Many2one('res.currency', related='product_id.forein_currency_id')
    forein_price_unit = fields.Monetary(compute='_compute_forein_price_unit', string='Forein price unit', readonly=True,
                                        store=True)

    @api.depends('price_unit')
    def _compute_forein_price_unit(self):
        for line in self:
            forein_price_unit = 0.0
            if not line.product_id:
                line.forein_price_unit = forein_price_unit
                continue

            if line.order_id.pricelist_id and line.order_id.partner_id:
                forein_price_unit = line.order_id.pricelist_id._compute_price_rule([(line.product_id,
                                                                                     line.product_uom_qty or 1.0,
                                                                                     line.order_id.partner_id)],
                                                                                   forein_price_unit=True)
                forein_price_unit = forein_price_unit.get(line.product_id.id, [0])[0]
            line.forein_price_unit = forein_price_unit
