# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import xlsxwriter
import base64
from datetime import datetime, date
from odoo.tools.misc import formatLang


class WizardBackdate(models.TransientModel):
    _name = 'wizard.back.date'
    _description = "inventory valuation with MRP wizard"

    date = fields.Datetime('Date')
    note = fields.Char('Note')

    def go_back(self):
        active_ids = self.env['mrp.production'].sudo().browse(self.env.context['active_ids'])
        for rec in active_ids:
            rec.sudo().with_context(force_date=True).write(
                {
                    'date_planned_start':self.date,
                    'note':self.note,
                }
            )            
            domain = [('id', 'in', (rec.move_raw_ids + rec.move_finished_ids + rec.scrap_ids.move_id).stock_valuation_layer_ids.ids)]
            valuation_ids = self.env['stock.valuation.layer'].sudo().search(domain)
            params = [self.date,tuple(valuation_ids.ids)]
            if valuation_ids :
                query = """ update stock_valuation_layer set create_date = %s where id in %s """
                self.env.cr.execute(query, params)
                for v in valuation_ids :
                    v.account_move_id.button_draft()
                    v.account_move_id.write(
                        {
                            'name' : '/',
                            'date' : self.date
                        }
                    )
                    v.account_move_id.action_post()
            stock_move_line = self.env['stock.move.line'].sudo().search(['|', ('move_id.raw_material_production_id', '=', rec.id), ('move_id.production_id', '=', rec.id)])
            params = [self.date,tuple(stock_move_line.ids)]
            if stock_move_line :
                query = """ update stock_move_line set date = %s where id in %s """
                self.env.cr.execute(query, params)
