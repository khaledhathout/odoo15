# -*- coding: utf-8 -*-

from odoo import api, fields, models
# import goslate
# from translate import Translator

class PBank(models.Model):
    _inherit = 'res.partner.bank'

    iban = fields.Char('IBAN')

class res_partner(models.Model):
    _inherit = 'res.partner'
