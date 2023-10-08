# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_sale_config = fields.Boolean(
        'Enable Total number of Qty in Sale order')
    sh_invoice_config = fields.Boolean(
        'Enable Total number of Qty in Invoice')

    sh_print_sale_config = fields.Boolean(
        'Print Total number of Qty In Sale Report')
    sh_print_invoice_config = fields.Boolean(
        'Print Total number of Qty In Invoice Report')


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_sale_config = fields.Boolean(
        'Enable Total number of Qty in Sale order', related='company_id.sh_sale_config', readonly=False)
    sh_invoice_config = fields.Boolean(
        'Enable Total number of Qty in Invoice', related='company_id.sh_invoice_config', readonly=False)

    sh_print_sale_config = fields.Boolean(
        'Print Total number of Qty In Sale Report', related='company_id.sh_print_sale_config', readonly=False)
    sh_print_invoice_config = fields.Boolean(
        'Print Total number of Qty In Invoice Report', related='company_id.sh_print_invoice_config', readonly=False)
