# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot" 


    def name_get(self):
        result = []
        for lot in self:
            name = lot.name  +' ' +str(lot.product_qty) + ' ' + lot.product_uom_id.name
            result.append((lot.id, name))
        return result     