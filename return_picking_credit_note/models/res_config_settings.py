# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    difference_account_id = fields.Many2one(
        comodel_name='account.account', string='Difference Account', readonly=False, related="company_id.difference_account_id")

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account', readonly=False, related="company_id.analytic_account_id")



class ResCompany(models.Model):
    _inherit = 'res.company'

    difference_account_id = fields.Many2one(
        comodel_name='account.account', string='Difference Account')
    
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account')

