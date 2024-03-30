# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    """
    Overwrite to add an own printing layout
    """
    _inherit = "res.company"

    knowsystem_custom_layout = fields.Boolean(string="Custom Layout", default=False)
    external_layout_knowsystem_id = fields.Many2one("ir.ui.view", string="Article Layout")
