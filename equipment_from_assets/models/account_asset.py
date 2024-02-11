# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')

    def create_equipment(self):
        vals = {
            'name': self.name,
            'cost': self.original_value,
            'assign_date': self.acquisition_date,
            'effective_date': self.acquisition_date,
            'asset_id': self.id,
            # 'scrap_date': self.acquisition_date,
        }
        self.equipment_id = self.env['maintenance.equipment'].sudo().create(vals)
        return True
    
    def action_open_maintenance(self):
        action_window = {
            'name': _('Equipment'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.equipment',
            'views': [[False, 'tree'], [False, 'form']],
            'domain': [('id', 'in', self.equipment_id.ids)],
            'context': {
                'create': False,
            }
        }
        return action_window

class Equipment(models.Model):
    _inherit = 'maintenance.equipment'

    asset_id = fields.Many2one('account.asset', string='Equipment')

    def action_open_assets(self):
        action_window = {
            'name': _('Asset'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset',
            'views': [[False, 'tree'], [False, 'form']],
            'domain': [('id', 'in', self.asset_id.ids)],
            'context': {
                'create': False,
            }
        }
        return action_window