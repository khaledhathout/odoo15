# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class StockMOve(models.Model):
    _inherit = "stock.move"

    def _update_reserved_quantity(self, need, available_quantity, location_id, lot_id=None, package_id=None, owner_id=None, strict=True):
        """ Create or update move lines.
        """
        if self.sale_line_id and self.sale_line_id.lot_id:
            lot_id = self.sale_line_id.lot_id
            strict=True        
        return super(StockMOve,self)._update_reserved_quantity(need, available_quantity, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)

    def _get_available_quantity(self, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False):
        self.ensure_one()
        if self.sale_line_id and self.sale_line_id.lot_id:
            lot_id = self.sale_line_id.lot_id
            strict=True        
        return super(StockMOve,self)._get_available_quantity(location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict, allow_negative=allow_negative)
