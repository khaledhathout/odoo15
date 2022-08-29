# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,tools


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        ref = self.picking_id.name
        

        if self.raw_material_production_id :

            
            unit_material_cost = self.raw_material_production_id.total_actual_material_cost
                
            
            move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(qty, abs(unit_material_cost), credit_account_id, debit_account_id,description)



        elif self.production_id :
            total_qty = 0
            product_qty = 0
            for line in self.production_id.finished_move_line_ids :
                if line.product_id.id == self.product_id.id :
                    product_qty = product_qty + line.qty_done

                total_qty = line.qty_done + total_qty

            price_unit = self.production_id.total_actual_all_cost / total_qty

            cost = price_unit * product_qty


            move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(qty, abs(cost), credit_account_id, debit_account_id,description)

        else : 

            move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        

        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': description,
                'stock_move_id': self.id,
                'stock_valuation_layer_ids': [(6, None, [svl_id])],
                'move_type': 'entry',
            })
            new_account_move._post()
