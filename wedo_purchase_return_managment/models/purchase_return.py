# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tests import Form

class PurchaseReturn(models.Model):
    _name = 'purchase.return'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Purchase return management"
    _order = 'id desc'


    @api.model
    def _get_default_journal(self):
        journal = self.env['account.journal'].sudo().search([('type','=','purchase'),('company_id','=',self.env.company.id)], limit=1)
        if journal:
            return journal

    @api.model
    def _get_picking_type(self):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', self.env.company.id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    name = fields.Char(string="Name",copy=False, readonly=True, default=lambda x: _('New'))
    date_order = fields.Datetime('Order Date', required=True, default=fields.Datetime.now())
    p_order_id = fields.Many2one('purchase.order',string="Purchase Order", track_visibility='always')
    location_id = fields.Many2one('stock.location',string="Return Location", track_visibility='always')
    picking_ids = fields.One2many('stock.picking','return_id',string="Return Picking", track_visibility='always')
    partner_id = fields.Many2one("res.partner" ,string='Vendor',track_visibility='always',required=True)
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='State', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    order_line_ids = fields.One2many('purchase.return.line', 'order_id', string='Return Lines',
                                     states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    return_journal_id = fields.Many2one('account.journal', string='Return Journal',required=True,default=_get_default_journal)
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    picking_count = fields.Integer(string='Picking', compute='_compute_invoice_count')
    purchase = fields.Boolean(string="Purchase Order")
    currency_id = fields.Many2one("res.currency",  string="Currency", default=lambda self: self.env.company.currency_id.id)
    invoice_ids = fields.One2many('account.move','return_id',string="Invoice")
    location_id = fields.Many2one('stock.location', 'Receive To')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    picking_type_id = fields.Many2one('stock.picking.type', 'Receive To',
                                      required=True, default=_get_picking_type,domain=[('code', '=', 'outgoing')])
    default_location_dest_id_usage = fields.Selection(related='picking_type_id.default_location_dest_id.usage',
                                                      string='Destination Location Type',
                                                      readonly=True)

    total = fields.Monetary(compute='_compute_total_amount', store=True, currency_field='currency_id')
    amount_tax = fields.Monetary(compute='_compute_total_amount', string="Tax", store=True,
                                 currency_field='currency_id')
    amount_untax = fields.Monetary(compute='_compute_total_amount', string="Amount Un Tax", store=True,
                                   currency_field='currency_id')


    @api.depends('order_line_ids.price_subtotal', 'order_line_ids.tax_id')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount_untax = sum(rec.order_line_ids.mapped('price_subtotal')) if rec.order_line_ids else 0.0
            rec.amount_tax = sum(rec.order_line_ids.mapped('price_tax')) if rec.order_line_ids else 0.0
            rec.total = sum(rec.order_line_ids.mapped('price_subtotal')) + rec.amount_tax if rec.order_line_ids else 0.0

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft','cancel']:
                raise ValidationError(_("You can not delete confirmed Requests"))
            else:
                return super(PurchaseReturn,rec).unlink()

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('purchase.return.sequence') or _('New')
        return super(PurchaseReturn, self).create(vals)

    def _compute_invoice_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)
            rec.invoice_count = len(rec.invoice_ids)


    def action_open_picking_invoice(self):

        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.ids),],
            'context': {'create': False},
            'target': 'current'
        }

    def action_open_picking(self):
        return {
            'name': 'Picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.picking_ids.ids)],
            'target': 'current'
        }

        # To Print Purchase Return From Button

    def action_report_purchase_order(self):
        return self.env.ref('purchase.action_report_purchase_order').report_action(self)


    @api.onchange('p_order_id','purchase')
    def get_line(self):
        for rec in self:
            if rec.purchase:
                if rec.p_order_id:
                    rec.order_line_ids= False
                    rec.currency_id= False
                    lines =[]
                    for order in rec.p_order_id.order_line:
                        vals = self.get_line_vals(order)
                        lines.append((0, 0, vals))
                    rec.write({'order_line_ids':lines,'currency_id':rec.p_order_id.currency_id.id})
            else:
                rec.order_line_ids = False
                rec.p_order_id = False

    def get_line_vals(self,order):
        vals = {
            'purchase_order_id': order.id,
            'name': order.name,
            'display_type': order.display_type if order.display_type in ['line_section',
                                                                         'line_note'] else False,
            'product_id': order.product_id.id,
            'product_qty': order.product_qty,
            'product_uom': order.product_uom.id,
            'price_unit': order.price_unit,
        }
        return vals

    @api.onchange('partner_id')
    def chang_partner(self):
        for rec in self:
            rec.order_line_ids = False
            rec.p_order_id = False

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_process(self):
        if self.order_line_ids:
            returns = self.order_line_ids.filtered(lambda r:r.qty_return > 0 and r.display_type == False)
            if returns:
                self.create_picking_returns(returns)
            else:
                raise ValidationError(_("No line to return picking"))
            self.state = 'done'
        else:
            raise ValidationError(_("No lines"))

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done' and rec.picking_ids.filtered(lambda r:r.state == 'done'):
                raise ValidationError(_("You can not cancel processed request"))
            else:
                rec.state = "cancel"
                picks = rec.picking_ids.filtered(lambda r:r.state not in ['done','cancel'])
                if picks:
                    for picking_id in picks:
                        picking_id.sudo().action_cancel()

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'done' and rec.picking_ids.filtered(lambda r:r.state == 'done'):
                raise ValidationError(_("You can not reset processed request"))
            else:
                rec.state = 'draft'

    def creat_pick(self):
        data = {
            'location_id': self.picking_type_id.default_location_src_id.id,
            'location_dest_id':  self.partner_id.property_stock_supplier.id if self.partner_id.property_stock_supplier
            else self.picking_type_id.default_location_dest_id.id,
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'is_return': True,
            'return_id':  self.id,
            'origin':  self.name,
        }
        return data

    def create_picking_returns(self,returns_line):
        data = self.creat_pick()
        customer_picking = self.env['stock.picking'].sudo().create(data)
        for re in returns_line:
            vals = self.get_stock_vals(customer_picking,re)
            customer_move = self.env['stock.move'].sudo().create(vals)
        customer_picking.sudo().action_assign()

    def get_stock_vals(self,customer_picking,re):
        vals = {
                'name': 'move out',
                'location_id':self.picking_type_id.default_location_src_id.id,
                'location_dest_id':  self.partner_id.property_stock_supplier.id if self.partner_id.property_stock_supplier
                else self.picking_type_id.default_location_dest_id.id,
                'product_id': re.product_id.id,
                'product_uom': re.product_uom.id,
                'price_unit': re.price_unit,
                'product_uom_qty': re.qty_return,
                'picking_id': customer_picking.id,
                'return_line_id': re.id,
            }
        return vals

class PurchaseReturnLine(models.Model):
    _name = 'purchase.return.line'

    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Po Quantity', digits='Product Unit of Measure')
    product_id = fields.Many2one('product.product',string='Product',)
    order_id = fields.Many2one('purchase.return', string='Return Order', index=True,
                               ondelete='cascade')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Text(string='Description', required=True)
    purchase_order_id = fields.Many2one('purchase.order.line', string='Purchase Order',)
    state = fields.Selection(related='order_id.state', store=True, )
    qty_return = fields.Float("Return Qty", digits='Product Unit of Measure',)
    delivered_qty = fields.Float("Delivered Qty",compute="get_qty_amount",store=True, digits='Product Unit of Measure')
    invoiced_qty = fields.Float("Invoiced Qty",compute="get_qty_amount",store=True, digits='Product Unit of Measure')

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date')
    tax_id = fields.Many2many('account.tax', string='Taxes',)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Unit Price', digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', currency_field='currency_id',string='Subtotal', store=True)
    currency_id = fields.Many2one("res.currency", related='order_id.currency_id', string="Currency", store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)



    @api.depends('order_id.invoice_ids','order_id.picking_ids','order_id.picking_ids.state')
    def get_qty_amount(self):
        for rec in self:
            rec.invoiced_qty = sum(rec.order_id.invoice_ids.invoice_line_ids.filtered(lambda r:r.return_line_id == rec ).mapped('quantity'))
            rec.delivered_qty = sum( rec.order_id.picking_ids.move_ids_without_package.filtered(lambda r:r.return_line_id == rec and r.picking_id.state=='done').mapped('quantity_done'))

    @api.depends('qty_return', 'product_id', 'price_unit','currency_id','tax_id')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit
            line.price_subtotal = line.qty_return * price
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.qty_return,
                                            product=line.product_id, partner=line.order_id.partner_id)
            line.price_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))

    @api.onchange('product_id')
    def get_unit_uom(self):
        self.product_uom = self.product_id.uom_id.id
        self.price_unit = self.product_id.lst_price
        self.name = self.product_id.name if self.product_id else ""

    def get_invoice_state(self):
        for rec in self:
            invoice_state = ""
            if rec.order_id.invoice_ids:
                if rec.order_id.invoice_ids[0].payment_state == "not_paid":
                    invoice_state = "Not Paid"
                elif rec.order_id.invoice_ids[0].payment_state == "in_payment":
                    invoice_state = "In Payment"
                elif rec.order_id.invoice_ids[0].payment_state == "paid":
                    invoice_state = "Paid"
                elif rec.order_id.invoice_ids[0].payment_state == "partial":
                    invoice_state = "Partial Paid"
                elif rec.order_id.invoice_ids[0].payment_state == "reversed":
                    invoice_state = "Reversed"
                else:
                    invoice_state = "Invoicing App Legacy"
            return invoice_state

    def get_invoice_discount(self):
        for rec in self:
            discount_amount = 0.0
            invoice_lines_discount = sum(self.env['account.move.line'].search([('return_line_id', '=', rec.id)]).mapped('discount'))
            discount_amount = (rec.price_subtotal * (invoice_lines_discount / 100))
            return discount_amount





class AccountMove(models.Model):
    _inherit = 'account.move'

    picking_id = fields.Many2one('stock.picking', string='Picking')
    return_id = fields.Many2one('purchase.return', string='Return')

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    return_line_id = fields.Many2one('purchase.return.line', string='Return')

