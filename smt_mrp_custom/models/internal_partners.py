from odoo import fields, models, api


class accountmoveline(models.Model):
    _inherit = 'account.move.line'
    _description = 'Description'

    @api.onchange('partner_id')
    def partner_id_change(self):
        internal_partners = self.env['res.company'].sudo().search([('partner_id', '!=', False)]).mapped(
            'partner_id')
        if self.partner_id.id in internal_partners.ids:
            res = {}
            res['domain'] = {'account_id': [('user_type_id', 'not in',
                                             (self.env.ref('account.data_account_type_direct_costs').id,
                                              self.env.ref('account.data_account_type_revenue').id
                                              , self.env.ref('account.data_account_type_other_income').id
                                              , self.env.ref('account.data_account_type_expenses').id,))]}
            self.tax_ids = False
            return res
