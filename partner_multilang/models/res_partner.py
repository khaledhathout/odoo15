# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(index=True, translate=True)

