# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, _
from odoo.tools import float_round
from odoo.tools import float_is_zero, OrderedSet


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one("account.analytic.account", string="Analytic Account")


    # @override

    def _action_done(self, cancel_backorder=False):
        """Call _account_entry_move for internal moves as well."""
        res = super()._action_done(cancel_backorder=False)
        for move in res:
            # first of all, define if we need to even valuate something
            if move.product_id.valuation != 'real_time':
                continue
            # we're customizing behavior on moves between internal locations
            # only, thus ensuring that we don't clash w/ account moves
            # created in `stock_account`
            if not move._is_internal():
                continue
            move._account_entry_move(1, "test", 11, 22)
        return res

    def _get_in_move_lines(self):
        """ Returns the `stock.move.line` records of `self` considered as incoming. It is done thanks
        to the `_should_be_valued` method of their source and destionation location as well as their
        owner.

        :returns: a subset of `self` containing the incoming records
        :rtype: recordset
        """
        res = super(StockMove, self)._get_in_move_lines()
        self.ensure_one()
        res = OrderedSet()
        for move_line in self.move_line_ids:
            if move_line.owner_id and move_line.owner_id != move_line.company_id.partner_id:
                continue
            if not move_line.location_id._should_be_valued() and move_line.location_dest_id._should_be_valued():
                res.add(move_line.id)
            if move_line.location_id._should_be_valued() and move_line.location_dest_id._should_be_valued():
                res.add(move_line.id)

        return self.env['stock.move.line'].browse(res)

    # @override

    def _run_valuation(self, quantity=None):
        # Extend `_run_valuation` to make it work on internal moves.
        self.ensure_one()
        res = super()._run_valuation(quantity)
        if self._is_internal() and not self.value:
            # TODO: recheck if this part respects product valuation method
            self.value = float_round(
                value=self.product_id.standard_price * self.quantity_done,
                precision_rounding=self.company_id.currency_id.rounding,
            )
        return res

    # @override

    def _account_entry_move(self):
        self.ensure_one()
        res = super(StockMove, self)._account_entry_move(1, 'test', 11, 220)
        if res is not None and not res:
            # `super()` tends to `return False` as an indicator that no
            # valuation should happen in this case
            return res

        # treated by `super()` as a self w/ negative qty due to this hunk:
        # quantity = self.product_qty or context.get('forced_quantity')
        # quantity = quantity if self._is_in() else -quantity
        # so, self qty is flipped twice and thus preserved
        self = self.with_context(forced_quantity=-self.product_qty)

        location_from = self.location_id
        location_to = self.location_dest_id

        # get valuation accounts for product
        if self._is_internal():
            product_valuation_accounts \
                = self.product_id.product_tmpl_id.get_product_accounts()
            stock_valuation = product_valuation_accounts.get('stock_valuation')
            stock_journal = product_valuation_accounts.get('stock_journal')

            if location_from.force_accounting_entries \
                    and location_to.force_accounting_entries:
                self._create_account_move_line(
                    self.picking_id.account_id.id,
                    self.product_id.categ_id.property_stock_valuation_account_id.id
                    ,
                    stock_journal.id)
            elif location_from.force_accounting_entries:
                self._create_account_move_line(
                    self.picking_id.account_id.id,
                    self.product_id.categ_id.property_stock_valuation_account_id.id,
                    stock_journal.id)
            elif location_to.force_accounting_entries:
                self._create_account_move_line(
                    self.picking_id.account_id.id,
                    self.product_id.categ_id.property_stock_valuation_account_id.id,
                    stock_journal.id)

        return res

    def _account_entry_move(self, qty, description, svl_id, cost):
        self = self.with_context(analytic=self.analytic_account_id.id)
        """ Accounting Valuation Entries """
        if self.picking_id.code != 'internal':
            return super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)
        print('\n'*3,self.product_id.categ_id.read(),'\n'*3)
        valuation_account = self.product_id.categ_id.property_stock_valuation_account_id.id
        self.ensure_one()
        am_vals = []
        if self.product_id.type != 'product':
            # no stock valuation for consumable products
            return am_vals
        if self.restrict_partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return am_vals

        company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False
        journal_id, line_account, expense_account, acc_valuation = self._get_accounting_data_for_valuation()
        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        expense_account =self.product_id.categ_id.property_stock_valuation_account_id
        line_account = self.picking_id.account_id
        if self._is_in() and self.picking_id.is_internal_move:
            if self.mapped('move_line_ids.location_id.usage') and self.mapped(
                    'move_line_ids.location_dest_id.usage') == 'internal':
                am_vals.append(
                    self.with_company(company_to)._prepare_account_move_vals(
                        self.product_id.categ_id.property_stock_valuation_account_id.id, acc_valuation,
                        journal_id, qty,
                        description, svl_id, cost))
            if self.origin_returned_move_id and self.picking_id.code == 'internal':
                l_a = self.picking_id.account_id.id
                r_a = self.product_id.categ_id.property_stock_valuation_account_id.id
                am_vals.append(
                    self.with_company(company_to)._prepare_account_move_vals(l_a, r_a,
                                                                             journal_id, qty, description, svl_id,
                                                                             cost))
            else:
                l_a = self.picking_id.account_id.id
                r_a = self.product_id.categ_id.property_stock_valuation_account_id.id
                am_vals.append(
                    self.with_company(company_to)._prepare_account_move_vals(r_a, l_a, journal_id, qty,
                                                                             description, svl_id, cost))

        # Create Journal Entry for products leaving the company
        if self._is_out() and self.picking_id.is_internal_move:
            cost = -1 * cost
            if self.origin_returned_move_id and self.picking_id.code != 'internal':
                l_a = self.picking_id.account_id.id
                r_a = self.product_id.categ_id.property_stock_valuation_account_id.id
                am_vals.append(
                    self.with_company(company_from)._prepare_account_move_vals(r_a, l_a, journal_id, qty,
                                                                               description, svl_id, cost))
            else:
                l_a = self.picking_id.account_id.id
                r_a = self.product_id.categ_id.property_stock_valuation_account_id.id
                am_vals.append(
                    self.with_company(company_from)._prepare_account_move_vals(r_a, l_a,
                                                                               journal_id, qty, description, svl_id,
                                                                               cost))

        if self.company_id.anglo_saxon_accounting and self.picking_id.is_internal_move:
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            if self._is_dropshipped():
                if cost > 0:
                    am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(acc_src, acc_valuation,
                                                                                                 journal_id, qty,
                                                                                                 description, svl_id,
                                                                                                 cost))
                else:
                    cost = -1 * cost
                    am_vals.append(
                        self.with_company(self.company_id)._prepare_account_move_vals(acc_valuation, valuation_account,
                                                                                      journal_id, qty, description,
                                                                                      svl_id, cost))
            elif self._is_dropshipped_returned():
                if cost > 0:
                    am_vals.append(self.with_company(self.company_id)._prepare_account_move_vals(acc_valuation, acc_src,
                                                                                                 journal_id, qty,
                                                                                                 description, svl_id,
                                                                                                 cost))
                else:
                    cost = -1 * cost
                    am_vals.append(
                        self.with_company(self.company_id)._prepare_account_move_vals(valuation_account, acc_valuation,
                                                                                      journal_id, qty, description,
                                                                                      svl_id, cost))

        return am_vals

    def _is_internal(self):
        self.ensure_one()
        return self.location_id.usage == 'internal' \
               and self.location_dest_id.usage == 'internal'

    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        if self.picking_id.code != 'internal':
            return super(StockMove, self)._get_accounting_data_for_valuation()
        valuation_account = self.product_id.categ_id.property_stock_valuation_account_id.id
        journal_id, expense_account, valuation_account, acc_valuation \
            = super()._get_accounting_data_for_valuation()

        expense_account = self.product_id.categ_id.property_stock_valuation_account_id
        # intercept account valuation, use account specified on internal
        # location as a local valuation
        if self._is_in() and self.location_dest_id.force_accounting_entries:

            acc_valuation \
                = self.picking_id.account_id.id
        if self._is_out() and self.location_id.force_accounting_entries:
            acc_valuation \
                = self.picking_id.account_id.id
        return journal_id, self.product_id.categ_id.property_stock_valuation_account_id.id, valuation_account, acc_valuation

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        analytic = self.env.context.get('analytic',False)
        print('\n'*3,analytic,'\n'*3)
        # if analytic:
        self.ensure_one()
        if debit_account_id != self.product_id.categ_id.property_stock_valuation_account_id.id:
            debit_line_vals = {
                'name': description,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'debit': debit_value if debit_value > 0 else 0,
                'credit': -debit_value if debit_value < 0 else 0,
                'account_id': debit_account_id,
                'analytic_account_id': analytic,
            }
            credit_line_vals = {
                'name': description,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': credit_value if credit_value > 0 else 0,
                'debit': -credit_value if credit_value < 0 else 0,
                'account_id': credit_account_id,
                # 'analytic_account_id': analytic,
            }
        else:
            debit_line_vals = {
                'name': description,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'debit': debit_value if debit_value > 0 else 0,
                'credit': -debit_value if debit_value < 0 else 0,
                'account_id': debit_account_id,
                # 'analytic_account_id': analytic,
            }
            credit_line_vals = {
                'name': description,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': credit_value if credit_value > 0 else 0,
                'debit': -credit_value if credit_value < 0 else 0,
                'account_id': credit_account_id,
                'analytic_account_id': analytic,
            }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
                'analytic_account_id': analytic,
            }
        return rslt



class picking(models.Model):
    _inherit = 'stock.picking'

    code = fields.Selection(related="picking_type_id.code", string="code", store=True)
    account_id = fields.Many2one("account.account", string="Account")
    is_internal_move = fields.Boolean(string="Create Internal Move", default=False)


    def _action_done(self):
        """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
        This method makes sure every `stock.move.line` is linked to a `stock.move` by either
        linking them to an existing one or a newly created one.

        If the context key `cancel_backorder` is present, backorders won't be created.

        :return: True
        :rtype: bool
        """
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(
            lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        for picking in self:
            if picking.owner_id:
                picking.move_lines.write({'restrict_partner_id': picking.owner_id.id})
                picking.move_line_ids.write({'owner_id': picking.owner_id.id})
        todo_moves._action_done()
        self.write({'date_done': fields.Datetime.now(), 'priority': '0'})

        # if incoming moves make other confirmed/partially_available moves available, assign them
        done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code == 'incoming').move_lines.filtered(
            lambda m: m.state == 'done')
        done_incoming_moves._trigger_assign()

        self._send_confirmation_email()
        return True
