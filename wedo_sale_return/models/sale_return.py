# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class SaleReturn(models.Model):
    _name = 'sale.return'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "sale return management"
    _order = 'id desc'

    @api.model
    def _get_default_journal(self):
        journal = self.env['account.journal'].sudo().search(
            [('type', '=', 'sale'), ('company_id', '=', self.env.company.id)], limit=1)
        if journal:
            return journal

    @api.onchange('location_id')
    def _get_picking_type(self):
        if not self.location_id:
            self.picking_type_id = False
        else:
            warehouse = self.location_id.warehouse_id
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'outgoing'), ('warehouse_id', '=', warehouse.id)], limit=1).return_picking_type_id
            if not picking_type:
                picking_type = self.env['stock.picking.type'].search(
                    [('code', '=', 'incoming'), ('default_location_dest_id', '=', self.location_id.id)], limit=1)
            self.picking_type_id = picking_type and picking_type.id
        return {'domain': {'picking_type_id': [('code', '=', 'incoming'), ('default_location_dest_id', '=', self.location_id.id)]}}

    name = fields.Char(
        string="Name", copy=False, readonly=True, default=lambda x: _('New')
    )
    date_order = fields.Datetime(
        'Date', required=True, default=fields.Datetime.now()
    )
    sale_order_id = fields.Many2one(
        'sale.order', string="Sale Order", track_visibility='always'
    )
    effective_date = fields.Datetime(related='sale_order_id.effective_date')
    location_id = fields.Many2one(
        'stock.location', string="Return Location", track_visibility='always'
    )
    picking_ids = fields.One2many(
        'stock.picking', 'sale_return_id', string="Return Picking", track_visibility='always'
    )
    partner_id = fields.Many2one(
        "res.partner", string='Customer', track_visibility='always', required=True
    )
    user_id = fields.Many2one(
        'res.users', string='Responsible', required=False, default=lambda self: self.env.user
    )
    type = fields.Selection(
        [('return', 'Return'), ('exchange', 'Exchange')], default='return', required=True
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancelled')],
        string='State', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange'
    )
    order_line_ids = fields.One2many(
        'sale.return.line', 'order_id', string='Return Lines',
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True
    )
    return_journal_id = fields.Many2one(
        'account.journal', string='Return Journal', required=True, default=_get_default_journal
    )
    invoice_count = fields.Integer(
        string='Invoices', compute='_compute_counts'
    )
    picking_count = fields.Integer(
        string='Picking', compute='_compute_counts'
    )
    sale = fields.Boolean(
        string="From Sale Order", default=True
    )
    invoice_ids = fields.One2many(
        'account.move', 'sale_return_id', string="Invoice"
    )
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True, copy=False, default=lambda self: self.env.company.id
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Receive To'
    )
    default_location_dest_id_usage = fields.Selection(
        related='picking_type_id.default_location_dest_id.usage',
        string='Destination Location Type', readonly=True
    )
    reason_id = fields.Many2one(
        'sale.return.reason', string="Reason", required=True, track_visibility='always'
    )
    reference = fields.Char(
        string="Reference", track_visibility='always', copy=False
    )
    total = fields.Monetary(
        compute='_compute_total_amount', store=True, currency_field='currency_id'
    )
    amount_tax = fields.Monetary(
        compute='_compute_total_amount', string="Tax", store=True, currency_field='currency_id'
    )
    amount_untax = fields.Monetary(
        compute='_compute_total_amount', string="Amount Un Tax", store=True, currency_field='currency_id'
    )
    exchange_order_total = fields.Monetary(
        related='exchange_order_id.amount_total'
    )
    net_amount = fields.Monetary(
        compute='_compute_total_amount'
    )
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected."
    )
    currency_id = fields.Many2one(
        related='pricelist_id.currency_id', depends=["pricelist_id"], store=True
    )
    show_update_pricelist = fields.Boolean(
        string='Has Pricelist Changed',
        help="Technical Field, True if the pricelist was changed;\n"
             " this will then display a recomputation button"
    )
    approval_reason = fields.Selection(
        [('not_open', 'Doesn\'t Open Yet'), ('all_component', 'Opened, But with all Component'), ('other', 'Other')]
    )
    other_reason = fields.Char()
    services = fields.Many2many("product.product", string="Fsm Services")
    # fsm_project_ids = fields.Many2many(
    #     "project.project",compute='_compute_fsm_project_ids', copy=False, string="Fsm Projects"
    # )
    task_ids = fields.One2many(
        'project.task', 'sale_return_id', string="Return FS", track_visibility='always'
    )
    task_count = fields.Integer(
        string='Tasks', compute='_compute_counts'
    )
    exchange_order_id = fields.Many2one(
        'sale.order', string="Exchange Order", track_visibility='always'
    )
    paid = fields.Boolean(compute='_compute_paid')
    analytic_account_id = fields.Many2one('account.analytic.account')

    @api.depends('exchange_order_id.invoice_ids.payment_state', 'invoice_ids.payment_state')
    def _compute_paid(self):
        for rec in self:
            if rec.state == 'done' and \
               not rec.invoice_ids.filtered(lambda inv: inv.payment_state != 'paid') and \
               rec.exchange_order_id.invoice_status == 'invoiced' and \
               not rec.exchange_order_id.invoice_ids.filtered(lambda inv: inv.payment_state != 'paid'):
                rec. paid = True
            else:
                rec.paid = False

    # @api.depends('order_line_ids.product_id')
    # def _compute_fsm_project_ids(self):
    #     for order in self:
    #         projects = order.order_line_ids.mapped('product_id.categ_id.fsm_department')
    #         order.fsm_project_ids = projects


    @api.onchange('pricelist_id', 'order_line_ids')
    def _onchange_pricelist_id(self):
        if self.order_line_ids and self.pricelist_id and not self.sale and self.partner_id.property_product_pricelist != self.pricelist_id:
            self.show_update_pricelist = True
        else:
            self.show_update_pricelist = False

    _sql_constraints = [
        ('reference_uniq', 'unique (reference)', "This Reference already exists !"),
    ]

    @api.depends('order_line_ids.price_subtotal', 'order_line_ids.tax_id', 'exchange_order_total')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount_untax = sum(rec.order_line_ids.mapped('price_subtotal')) if rec.order_line_ids else 0.0
            rec.amount_tax = sum(rec.order_line_ids.mapped('price_tax')) if rec.order_line_ids else 0.0
            rec.total = sum(rec.order_line_ids.mapped('price_subtotal')) + rec.amount_tax if rec.order_line_ids else 0.0
            rec.net_amount = rec.total - rec.exchange_order_total


    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise ValidationError(_("You can not delete confirmed Requests"))
            else:
                return super(SaleReturn, rec).unlink()

    @api.model
    def create(self, vals):
        res = super(SaleReturn, self).create(vals)
        if not res.name or res.name == _('New'):
            res.name = self.env['ir.sequence'].sudo().next_by_code('sale.return.sequence') or _('New')
        return res

    def _compute_counts(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)
            rec.invoice_count = len(rec.invoice_ids)+self.exchange_order_id.invoice_count
            rec.task_count = len(rec.task_ids)

    def action_open_picking_invoice(self):
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.ids+self.exchange_order_id.invoice_ids.ids)],
            'context': {'create': False},
            'target': 'current'
        }

    def action_open_picking(self):
        return {
            'name': 'Picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('id', '=', self.picking_ids.ids)],
            'target': 'current'
        }

    def action_open_task(self):
        return {
            'name': 'Task',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('id', '=', self.task_ids.ids)],
            'target': 'current'
        }

    @api.onchange('sale_order_id', 'sale')
    def get_line(self):
        for rec in self:
            if rec.sale and rec.sale_order_id:
                rec.analytic_account_id = rec.sale_order_id.analytic_account_id.id
                rec.order_line_ids = False
                rec.currency_id = False
                lines = []
                for order in rec.sale_order_id.order_line.filtered(lambda l: l.product_id.detailed_type != 'service' and
                                                                             l.qty_delivered > l.qty_returned):

                    vals = self.get_line_vals(order)
                    lines.append((0, 0, vals))
                rec.write({'order_line_ids': lines, 'pricelist_id': rec.sale_order_id.pricelist_id.id})
            else:
                rec.order_line_ids = False
                rec.sale_order_id = False
                rec.analytic_account_id = False

    def get_line_vals(self, order):
        vals = {
            'sale_order_id': order.id,
            'name': order.name,
            'display_type': order.display_type if order.display_type in ['line_section', 'line_note'] else False,
            'product_id': order.product_id.id,
            'product_qty': order.qty_delivered - order.qty_returned,
            'qty_return': order.qty_delivered - order.qty_returned,
            'product_uom': order.product_uom.id,
            'tax_id': [(6, 0, order.tax_id.ids)],
            'price_unit': order.price_unit,
            'discount': order.discount,
            'discount_fixed': order.discount_fixed,
        }
        return vals

    @api.onchange('partner_id')
    def chang_partner(self):
        for rec in self:
            rec.order_line_ids = False
            rec.sale_order_id = False
            rec.pricelist_id = rec.partner_id.property_product_pricelist.id if not rec.sale else False

    @api.depends('type', 'date_order', 'effective_date')
    def onchange_type_date_order(self):
        if not self.check_return_exchange_period():
            type = (self.type == 'return' and _('Return')) or (self.type == 'exchange' and _('Exchange'))
            raise ValidationError(_("You have exceeded the grace period for %s") % type)

    def check_return_exchange_period(self):
        params = self.env['ir.config_parameter'].sudo()
        if self.effective_date and self.type == 'return':
            return_period = int(params.get_param('sale_return_period', default=3))
            if self.date_order > (self.effective_date + timedelta(days=return_period)):
                return False
        if self.effective_date and self.type == 'exchange':
            exchange_period = int(params.get_param('sale_exchange_period', default=7))
            if self.date_order > (self.effective_date + timedelta(days=exchange_period)):
                return False
        return True

    def action_confirm(self):
        for rec in self:
            if rec.type == 'exchange' and not rec.exchange_order_id:
                raise ValidationError(_("You have to add the exchange order"))
            if rec.check_return_exchange_period():
                rec.action_process()
            else:
                rec.state = 'confirm'

    def action_process(self):
        if self.order_line_ids:
            returns = self.order_line_ids.filtered(lambda r: r.qty_return > 0 and r.display_type == False)
            if returns:
                return_picking = self.create_picking_returns(returns)
                # self.create_fsm_task(returns, return_picking)
            else:
                raise ValidationError(_("No line to return picking"))
            self.state = 'done'
        else:
            raise ValidationError(_("No lines"))

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done' and rec.picking_ids.filtered(lambda r: r.state == 'done'):
                raise ValidationError(_("You can not cancel processed request"))
            else:
                rec.state = "cancel"
                picks = rec.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'])
                if picks:
                    for picking_id in picks:
                        picking_id.sudo().action_cancel()

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'done' and rec.picking_ids.filtered(lambda r: r.state == 'done'):
                raise ValidationError(_("You can not reset processed request"))
            else:
                rec.state = 'draft'

    def create_picking_returns(self, returns_line):
        data = self.create_pick()
        customer_picking = self.env['stock.picking'].sudo().create(data)
        for re in returns_line:
            vals = self.get_stock_vals(customer_picking, re)
            customer_move = self.env['stock.move'].sudo().create(vals)
        customer_picking.sudo().action_assign()
        return customer_picking

    def create_pick(self):
        data = {
            'location_id': self.picking_type_id.default_location_src_id.id if self.picking_type_id.default_location_src_id
            else self.partner_id.property_stock_customer.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'is_sale_return': True,
            'sale_return_id': self.id,
            'origin': self.name, }
        return data

    def get_stock_vals(self, customer_picking, re):
        vals = {
            'name': 'Sale Return',
            'location_id': self.partner_id.property_stock_customer.id if self.partner_id.property_stock_customer
            else self.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'product_id': re.product_id.id,
            'product_uom': re.product_uom.id,
            # 'price_unit': re.price_unit,
            'product_uom_qty': re.qty_return,
            'picking_id': customer_picking.id,
            'sale_return_line_id': re.id,
        }
        return vals

    '''def update_prices(self):
        self.ensure_one()
        lines_to_update = []
        for line in self.order_line_ids.filtered(lambda line: not line.display_type):
            product = line.product_id.with_context(
                partner=self.partner_id,
                quantity=line.qty_return,
                date=self.date_order,
                pricelist=self.pricelist_id.id,
                uom=line.product_uom.id
            )
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                line._get_display_price(product), line.product_id.taxes_id, line.tax_id, line.company_id)
            lines_to_update.append((1, line.id, {'price_unit': price_unit}))
        self.update({'order_line_ids': lines_to_update})
        self.show_update_pricelist = False
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ",
                                 self.pricelist_id.display_name))'''

    # def create_fsm_task(self, returns, return_picking):
    #     for srv in self.services:
    #         lines = returns.filtered(lambda r: r.product_id.categ_id.fsm_department == srv.project_id)
    #         if lines:
    #             task = self.env['project.task'].sudo().create({
    #                 'name': '%s: %s' % (self.name, srv.name),
    #                 'partner_id': self.partner_id.id,
    #                 'email_from': self.partner_id.email,
    #                 'project_id': srv.project_id.id,
    #                 'company_id': srv.project_id.company_id.id,
    #                 'user_ids': False,  # force non assigned task, as created as sudo()
    #                 'picking_id': return_picking.id,
    #                 'sale_return_id': self.id,
    #             })

                # task_msg = _("This task has been created from: <a href=# data-oe-model=sale.return data-oe-id=%d>%s</a> (%s)") % (self.id, self.name, srv.name)
                # task.message_post(body=task_msg)
                # for l in lines:
                #     self.env['fsm.lines'].create({
                #         'product_id': l.product_id.id,
                #         'service_id': srv.id,
                #         'task_id': task,
                #         'qty': l.qty_return,
                #     })

    def add_exchange_order(self):
        self.exchange_order_id = self.sale_order_id.copy({
            'date_order': self.date_order,
            'order_line': False,
        })
        for line in self.order_line_ids:
            line.sale_order_id.copy({
                'order_id':  self.exchange_order_id.id,
                'product_uom_qty': line.qty_return,
            })
        return {
            'name': 'Exchange Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': self.exchange_order_id.id,
            'target': 'current'
        }


class SaleReturnLine(models.Model):
    _name = 'sale.return.line'

    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Sale Quantity', digits='Product Unit of Measure')
    product_id = fields.Many2one('product.product', string='Product')
    order_id = fields.Many2one('sale.return', string='Return Order', index=True,
                               ondelete='cascade')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Text(string='Description', required=True)

    sale_order_id = fields.Many2one('sale.order.line', string='Sale Order line', )
    state = fields.Selection(related='order_id.state', store=True, )
    qty_return = fields.Float("Return Qty", digits='Product Unit of Measure')
    received_qty = fields.Float("Received Qty", compute="get_qty_amount", store=True, digits='Product Unit of Measure')
    invoiced_qty = fields.Float("Invoiced Qty", compute="get_qty_amount", store=True, digits='Product Unit of Measure')
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date')
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Unit Price', digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', currency_field='currency_id',
                                     readonly=True, store=True)
    currency_id = fields.Many2one("res.currency", related='order_id.currency_id', string="Currency", readonly=True,
                                  store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, copy=False,
                                 related='order_id.company_id')
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    discount_fixed = fields.Float(string="Discount (Fixed)", digits="Product Price",
                                  help="Fixed amount discount from unit price.",
    )
    unit_qty = fields.Float(compute='_compute_unit_qty', string='Unit Qty')

    def _compute_unit_qty(self):
        for rec in self:
            width = rec.product_id.width
            length = rec.product_id.length
            height = rec.product_id.height

            rec.unit_qty = 0.0
            if rec.product_uom.equation == 'm2':
                rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or rec.qty_return == 0.0 else rec.qty_return / (
                        length * width)

            elif rec.product_uom.equation == 'm3':
                rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.qty_return == 0.0 else rec.qty_return / (
                        length * width * height)

            elif rec.product_uom.equation == 'lm':
                rec.unit_qty = 0.0 if length == 0.0 or rec.qty_return == 0.0 else rec.qty_return / length

            elif rec.product_uom.equation == 'qty' or not rec.product_uom.equation:
                rec.unit_qty = rec.qty_return

    @api.depends('order_id.invoice_ids', 'order_id.picking_ids', 'order_id.picking_ids.state')
    def get_qty_amount(self):
        for rec in self:
            rec.invoiced_qty = sum(
                rec.order_id.invoice_ids.invoice_line_ids.filtered(lambda r: r.sale_return_line_id == rec).mapped(
                    'quantity'))
            rec.received_qty = sum(rec.order_id.picking_ids.move_ids_without_package.filtered(
                lambda r: r.sale_return_line_id == rec and r.picking_id.state == 'done').mapped('quantity_done'))

    @api.depends("qty_return", "discount", "price_unit", "tax_id", "discount_fixed")
    def _compute_amount(self):
        for line in self:
            if line.tax_id.filtered(lambda t: t.price_include == True) and len(line.tax_id) > 1:
                raise ValidationError(
                    _("Tax included in price should use alone.")
                )
            price = line.price_unit
            if not line.tax_id.filtered(lambda t: t.price_include == True) and (line.discount or line.discount_fixed):
                price = price * (1 - (line.discount or 0.0) / 100.0) - (line.discount_fixed or 0.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.qty_return,
                                            product=line.product_id, partner=line.order_id.partner_id)

            if line.tax_id.filtered(lambda t: t.price_include == True):
                price_excl = line.qty_return and taxes['total_excluded'] / line.qty_return or 0
                if line.discount or line.discount_fixed:
                    price_excl_after_discount = price_excl * (1 - (line.discount or 0.0) / 100.0) - (
                                line.discount_fixed or 0.0)
                    taxes = line.tax_id.compute_all(price_excl_after_discount, line.order_id.currency_id,
                                                    line.qty_return,
                                                    product=line.product_id, partner=line.order_id.partner_id,
                                                    handle_price_include=False)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange('product_id')
    def get_unit_uom(self):
        self.product_uom = self.product_id.uom_id.id
        self.name = self.product_id.name if self.product_id else ""

    '''def _get_display_price(self, product):
        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id, uom=self.product_uom.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                               uom=self.product_uom.id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
            product or self.product_id, self.qty_return or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                           self.qty_return,
                                                                                           self.product_uom,
                                                                                           self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    _price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.order_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
                product_currency = product.cost_currency_id
            elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.company_id or self.env.company, self.order_id.date_order or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    @api.onchange('product_uom', 'qty_return', 'product_id', 'order_id.pricelist_id')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.qty_return,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)'''

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


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_return_id = fields.Many2one('sale.return', string='Return')
    picking_id = fields.Many2one("stock.picking", string="Picking")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sale_return_line_id = fields.Many2one('sale.return.line', string='Sale Return')

    def _stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()
        if self.move_id.move_type == 'out_refund' and self.move_id.picking_id and self.sale_return_line_id:
            scraps = self.env['stock.scrap'].search([('picking_id', '=', self.move_id.picking_id.id)])
            domain = [('product_id', '=', self.product_id.id),
                      ('id', 'in', (self.move_id.picking_id.move_lines + scraps.move_id).stock_valuation_layer_ids.ids)]
            valuation = self.env['stock.valuation.layer'].search(domain, limit=1)
            if valuation:
                price_unit = valuation.unit_cost

        return price_unit


class SaleReturnReason(models.Model):
    _name = 'sale.return.reason'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "sale return reason"
    _order = 'sequence'

    name = fields.Char(string="Reason", required=True, track_visibility='always')
    sequence = fields.Integer(string="Sequence", default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "This Reason already exists !"),
    ]


class Task(models.Model):
    _inherit = 'project.task'

    sale_return_id = fields.Many2one('sale.return')