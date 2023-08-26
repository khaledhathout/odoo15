# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    restrict_discount = fields.Boolean(string="Restrict Discount")
