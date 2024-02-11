from odoo import api, models, _
from odoo.exceptions import UserError
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_view_entry(self):
        journal_entry_ids = []

        vl_shortcut_dict = self.action_view_stock_valuation_layers()
        if 'domain' in vl_shortcut_dict:
            vl = self.env['stock.valuation.layer'].search(vl_shortcut_dict['domain'])
            if vl :
                journal_entry_ids+=vl.mapped('account_move_id.id')

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "context": {"create": False,"edit":False},
            "name": "Journal Entry",
            'view_mode': 'list,form',
            'domain':[('id','in',journal_entry_ids)]
        }