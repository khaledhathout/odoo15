from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class KsGlobalDiscountInvoice(models.Model):
    """ changing the model to account.move """
    _inherit = "account.move"

    ks_global_discount_type = fields.Selection([
        ('percent', 'Percentage'),
        ('amount', 'Amount')],
        string='Universal Discount Type',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
        default='percent')

    ks_global_discount_rate = fields.Float('Universal Discount',
                                           readonly=True,
                                           states={'draft': [('readonly', False)],
                                                   'sent': [('readonly', False)]})
    ks_amount_discount = fields.Monetary(string='Universal Discount',
                                         readonly=True,
                                         compute='ks_calculate_discount',
                                         store=True, track_visibility='always')

    ks_enable_discount = fields.Boolean(compute='ks_verify_discount')
    ks_sales_discount_account_id = fields.Integer(compute='ks_verify_discount')
    ks_purchase_discount_account_id = fields.Integer(compute='ks_verify_discount')
    compute_disc_line = fields.Boolean(string="discount line",default=False)

    @api.depends('company_id.ks_enable_discount')
    def ks_verify_discount(self):
        for rec in self:
            rec.ks_enable_discount = rec.company_id.ks_enable_discount
            rec.ks_sales_discount_account_id = rec.company_id.ks_sales_discount_account.id
            rec.ks_purchase_discount_account_id = rec.company_id.ks_purchase_discount_account.id

    @api.model
    def create(self,vals):
        res =[]
        if 'compute_disc_line' in vals and vals['compute_disc_line']==True:
            self = self.with_context(check_move_validity=False,skip_compute_disc=1) 
            res = super(KsGlobalDiscountInvoice,self).create(vals)
            res.with_context(skip_compute_disc=0).ks_calculate_discount()
            res._check_balanced()
        else:
            self = self.with_context(skip_compute_disc=1) 
            res = super(KsGlobalDiscountInvoice,self).create(vals)
        return res
    # @api.multi
    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'ks_global_discount_type',
        'ks_global_discount_rate')
    def ks_calculate_discount(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                line.global_discount=False
            if rec.invoice_line_ids.filtered(lambda x: x.tax_ids):
                rec.invoice_line_ids.filtered(lambda x: x.tax_ids)[0].global_discount =True

            if rec.ks_global_discount_type == "amount":
                rec.ks_amount_discount = rec.ks_global_discount_rate if rec.amount_untaxed > 0 else 0
            elif rec.ks_global_discount_type == "percent":
                if rec.ks_global_discount_rate != 0.0:
                    rec.ks_amount_discount = (rec.amount_untaxed) * rec.ks_global_discount_rate / 100
                else:
                    rec.ks_amount_discount = 0
                    return
            elif not rec.ks_global_discount_type:
                rec.ks_global_discount_rate = 0
                rec.ks_amount_discount = 0
                return
            for line in rec.invoice_line_ids:
                if line.global_discount:
                    line.update(line.with_context(discount=line.move_id.ks_amount_discount)._get_price_total_and_subtotal())
                else:
                    line.update(line._get_price_total_and_subtotal())

            rec._recompute_dynamic_lines(recompute_all_taxes=True)
            rec._compute_tax_totals_json()
            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.ks_amount_discount
            sign = rec.move_type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_signed = rec.amount_total * sign

            #rec.ks_update_universal_discount()

    @api.constrains('ks_global_discount_rate')
    def ks_check_discount_value(self):
        if self.ks_global_discount_type == "percent":
            if self.ks_global_discount_rate > 100 or self.ks_global_discount_rate < 0:
                raise ValidationError('You cannot enter percentage value greater than 100.')
        else:
            if self.ks_global_discount_rate < 0 or self.amount_untaxed < 0:
                raise ValidationError(
                    'You cannot enter discount amount greater than actual cost or value lower than 0.')

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        ks_res = super(KsGlobalDiscountInvoice, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                                      description=None, journal_id=None)
        ks_res['ks_global_discount_rate'] = self.ks_global_discount_rate
        ks_res['                                                                                                                                                                                        '] = self.ks_global_discount_type
        return ks_res


    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        """_summary_

        Args:
            recompute_all_taxes (bool, optional): _description_. Defaults to False.
            recompute_tax_base_amount (bool, optional): _description_. Defaults to False.
        """
        if self.env.context.get('skip_compute_disc','')!=1:
            self._recompute_universal_discount_lines()
        return super(KsGlobalDiscountInvoice,self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)

    def _recompute_universal_discount_lines(self):
        """This Function Create The General Entries for Universal Discount"""
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.ks_amount_discount == 0:
                already_exists = rec.line_ids.filtered(
                        lambda line: line.name and line.name.find('Universal Discount') == 0)
                rec.line_ids -= already_exists
            if rec.ks_global_discount_rate > 0 and rec.move_type in type_list:
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = self != self._origin
                    ks_name = "Universal Discount "
                    if rec.ks_global_discount_type == "amount":
                        ks_value = "of amount #" + str(self.ks_global_discount_rate)
                    elif rec.ks_global_discount_type == "percent":
                        ks_value = " @" + str(self.ks_global_discount_rate) + "%"
                    else:
                        ks_value = ''
                    ks_name = ks_name + ks_value
                    
                    already_exists = rec.line_ids.filtered(
                        lambda line: line.name and line.name.find('Universal Discount') == 0)
                    
                    amount = rec.ks_amount_discount
                    """The amount expressed in the secondary currency must
                    be positive when account is debited and negative when account is credited. 
                    If the currency is the same as the one from the company, this amount must strictly be equal to the balance."""


                    amount_currency = amount
                    if rec.currency_id != rec.company_id.currency_id:
                        amount = rec.currency_id._convert(amount_currency, rec.company_id.currency_id, rec.company_id, rec.date or rec.invoice_date)
                    
                    sign = rec.move_type in ["out_invoice", "in_invoice"] and 1 or -1
                    amount = sign * amount
                    #amount_currency = sign * amount_currency
                    
                    if already_exists:
                        if rec.move_type in ["out_invoice", "in_refund"]:
                            debit = amount > 0.0 and amount or 0.0,
                            credit = amount < 0.0 and -amount or 0.0,
                        else:
                            credit = amount > 0.0 and amount or 0.0,
                            debit = amount < 0.0 and -amount or 0.0,
                        if rec.ks_sales_discount_account_id \
                                and (rec.move_type in ["out_invoice", "out_refund"]):
                            
                            already_exists.update({
                                'name': ks_name,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                                'amount_currency': amount_currency,
                                'currency_id': rec.currency_id.id,
                            })
                            
                        if rec.ks_purchase_discount_account_id \
                                and (rec.move_type in ["in_invoice", "in_refund"]):
                            
                            already_exists.update({
                                'name': ks_name,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                                'amount_currency': - amount_currency if amount and amount > 0.0 else amount_currency,
                                'currency_id': rec.currency_id.id,
                            })
                            
                    else:
                        new_tax_line = self.env['account.move.line']
                        create_method = in_draft_mode and \
                                        self.env['account.move.line'].new or \
                                        self.env['account.move.line'].create
                        account_id = rec.move_type in ["out_invoice", "out_refund"] and rec.ks_sales_discount_account_id or rec.ks_purchase_discount_account_id
                        if rec.move_type in ["out_invoice", "in_refund"]:
                            debit = amount > 0.0 and amount or 0.0
                            credit = amount < 0.0 and -amount or 0.0
                        else:
                            credit = amount > 0.0 and amount or 0.0
                            debit = amount < 0.0 and -amount or 0.0
                        dict = {
                            'move_name': self.name,
                            'name': ks_name,
                            # 'price_unit': self.ks_amount_discount,
                            'quantity': 1,
                            'debit': debit,
                            'credit': credit,
                            'amount_currency': - amount_currency if amount and amount > 0.0 else amount_currency ,
                            'currency_id': rec.currency_id.id,
                            'account_id': account_id,
                            # 'move_id': self._origin,
                            'move_id': rec.id,
                            'date': rec.date,
                            'exclude_from_invoice_tab': True,
                            'partner_id': rec.partner_id and rec.partner_id.id or False,
                            'company_id': rec.company_id.id,
                            'company_currency_id': rec.company_currency_id.id,
                        }
                        candidate = create_method(dict)

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        """ Compute the dynamic tax lines of the journal entry.

        :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                is_refund = move.move_type in ('out_refund', 'in_refund')
                price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
            else:
                handle_price_include = False
                quantity = 1.0
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
                price_unit_wo_discount = base_line.amount_currency

            base_line_with_context = base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign())
            if base_line.global_discount:
                base_line_with_context=base_line.tax_ids._origin.with_context(discount=move.ks_amount_discount,force_sign=move._get_tax_force_sign())                
            return base_line_with_context.compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=move.always_tax_exigible,
            )

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tax_tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tax_tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line, tax_vals['group'])
                taxes_map_entry['grouping_dict'] = grouping_dict

        # ==== Pre-process taxes_map ====
        taxes_map = self._preprocess_taxes_map(taxes_map)

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # The tax line is no longer used in any base lines, drop it.
            if taxes_map_entry['tax_line'] and not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            currency = self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])

            # tax_base_amount field is expressed using the company currency.
            tax_base_amount = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id, self.company_id, self.date or fields.Date.context_today(self))

            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
                continue

            balance = currency._convert(
                taxes_map_entry['amount'],
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self),
            )
            to_write_on_line = {
                'amount_currency': taxes_map_entry['amount'],
                'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }

            if taxes_map_entry['tax_line']:
                # Update an existing tax line.
                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method({
                    **to_write_on_line,
                    'name': tax.name,
                    'move_id': self.id,
                    'company_id': self.company_id.id,
                    'company_currency_id': self.company_currency_id.id,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                taxes_map_entry['tax_line'].update(taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    global_discount = fields.Boolean(string="Global Discount")

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                continue
            if line.global_discount:
                line.update(line.with_context(discount=line.move_id.ks_amount_discount)._get_price_total_and_subtotal())
            else:
                line.update(line._get_price_total_and_subtotal())

            line.update(line._get_fields_onchange_subtotal())
