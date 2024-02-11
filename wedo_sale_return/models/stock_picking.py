# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tests import Form


class StockPicking(models.Model):
    _inherit = 'stock.move'

    sale_return_line_id = fields.Many2one('sale.return.line')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_sale_return = fields.Boolean(string="Sale Return")
    sale_return_id = fields.Many2one('sale.return')

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.company_id.sale_return_invoice_policy== 'order':
            rec.sudo().create_return_bill_from_order()
        return rec

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.sale_return_id and self.move_lines and self.state == 'done':
            invoice = self.sudo().sale_return_id.invoice_ids.filtered(lambda r: r.picking_id.id == self.id)
            if not invoice:
                self.sudo().create_sale_customer_bill()
        return res

    def create_return_bill_from_order(self):
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'incoming':
                sale_journal_id = picking_id.sale_return_id.return_journal_id.id
                invoice_line_list = []
                lines = picking_id.sale_return_id.order_line_ids.sudo().filtered(lambda r: r.qty_return > 0)
                notes = picking_id.sale_return_id.order_line_ids.sudo().filtered(lambda r: r.display_type != False)
                for l in lines:
                    vals = (0, 0, {
                        'name': l.product_id.name,
                        'product_uom_id':l.product_id.uom_id.id,
                        'product_id': l.product_id.id,
                        'price_unit': l.price_unit,
                        'tax_ids': [(6, 0, l.tax_id.ids)],
                        'quantity': l.qty_return,
                        'sale_return_line_id': l.id,
                        'discount': l.discount,
                        'discount_fixed': l.discount_fixed,
                        'analytic_account_id': picking_id.sale_return_id.analytic_account_id.id,
                        'account_id':picking_id.sale_return_id.return_journal_id.default_account_id.id

                    })
                    invoice_line_list.append(vals)
                if notes:
                    for n in notes:
                        vals = (0, 0, {
                            'name': n.name,
                            'display_type': n.display_type,
                        })
                        invoice_line_list.append(vals)
                if invoice_line_list:
                    value = self.get_lines(invoice_line_list,picking_id,current_user,sale_journal_id)
                    invoice = picking_id.env['account.move'].sudo().create(value)
                    invoice.action_post()

                    return invoice


    def create_sale_customer_bill(self):
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'incoming':
                sale_journal_id = picking_id.sale_return_id.return_journal_id.id
                invoice_line_list = []
                lines = picking_id.move_lines.sudo().filtered(lambda r: r.quantity_done > 0)
                notes = picking_id.sale_return_id.order_line_ids.sudo().filtered(lambda r: r.display_type != False)
                for move in lines:
                    if move.quantity_done > 0:
                        vals = (0, 0, {
                            'name': move.sale_return_line_id.product_id.name,
                            'product_uom_id':move.sale_return_line_id.product_id.uom_id.id,
                            'product_id': move.sale_return_line_id.product_id.id,
                            'price_unit': move.sale_return_line_id.price_unit,
                            'tax_ids': [(6, 0, move.sale_return_line_id.tax_id.ids)],
                            'quantity': move.quantity_done,
                            'sale_return_line_id': move.sale_return_line_id.id,
                            'discount': move.sale_return_line_id.discount,
                            'discount_fixed': move.sale_return_line_id.discount_fixed,
                            'analytic_account_id': picking_id.sale_return_id.analytic_account_id.id,
                            'account_id':picking_id.sale_return_id.return_journal_id.default_account_id.id
                        })
                        invoice_line_list.append(vals)
                if notes:
                    for n in notes:
                        vals = (0, 0, {
                            'name': n.name,
                            'display_type': n.display_type,
                        })
                        invoice_line_list.append(vals)
                if invoice_line_list:
                    value = self.get_lines(invoice_line_list,picking_id,current_user,sale_journal_id)
                    invoice = picking_id.env['account.move'].sudo().create(value)
                    invoice.action_post()
                    return invoice
                
    def get_lines(self,invoice_line_list,picking_id,current_user,sale_journal_id):
        value = {
                        'move_type': 'out_refund',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': current_user,
                        'partner_id': picking_id.partner_id.id,
                        'currency_id':  picking_id.sale_return_id.currency_id.id,
                        'journal_id': int(sale_journal_id),
                        'ref': "Sale Return %s" % picking_id.name,
                        'picking_id': picking_id.id,
                        'sale_return_id': picking_id.sale_return_id.id,
                        'invoice_line_ids': invoice_line_list
                    }
        return value
