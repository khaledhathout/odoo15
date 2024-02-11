

from odoo import fields, models, api, tools,_


class CurrencyInherit(models.Model):
    _inherit = 'res.currency'


    sar_rate = fields.Float('Saudi Riyal Rate')