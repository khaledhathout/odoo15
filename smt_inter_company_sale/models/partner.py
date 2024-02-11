# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner(self):
        # Delete tax if partner in intercompny rule
        for rec in self.order_line:
            rec.internal_company = False
        company = self.env['res.company']._find_company_from_partner(self.partner_id.id)
        if company and company.rule_type in ('sale', 'sale_purchase') and (not self.auto_generated):
            for rec in self.order_line:
                rec.internal_company = True
        for rec in self.order_line:
            rec._compute_tax_id()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    internal_company = fields.Boolean('Internal Company', default=False)

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(line.order_partner_id.id)
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda t: t.company_id == line.env.company)
            if line.internal_company:
                line.tax_id = False
            else:
                line.tax_id = fpos.map_tax(taxes)
