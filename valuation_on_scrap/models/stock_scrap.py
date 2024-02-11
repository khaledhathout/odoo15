# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    valuation_count = fields.Float('', compute="valuation_count_get")
    move_count = fields.Float('', compute="move_count_get")

    def valuation_count_get(self):
        for rec in self :
            rec.valuation_count = len(self.move_id.stock_valuation_layer_ids)

    def move_count_get(self):
        for rec in self :
            rec.move_count = len(self.move_id.stock_valuation_layer_ids.account_move_id)

    def view_valuation_layer(self):
        stock_valuation_layer_ids = self.move_id.stock_valuation_layer_ids.ids
        domain = [('id','in', stock_valuation_layer_ids)]
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_account.stock_valuation_layer_action")
        context = literal_eval(action['context'])
        context.update(self.env.context)
        context['no_at_date'] = True
        context['search_default_group_by_product_id'] = False
        return dict(action, domain=domain, context=context)

    def view_valuation_account_move(self):
        action = {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'views': [[False, 'tree'], [False, 'form'], [False, 'kanban']],
            'domain': [('id', 'in', self.move_id.stock_valuation_layer_ids.account_move_id.ids)],
            'context': {
                'create': False,
            }
        }
       
        return action
