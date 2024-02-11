# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    note = fields.Char('Note')

    def action_backdate(self):
        return{
            'name': _('Back Date'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.back.date',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'active_ids':self.ids},
            'target': 'new',
            'view_id': self.env.ref('mrp_order_backdate.wizard_inventory_valuation_form_view').id
            }
        
