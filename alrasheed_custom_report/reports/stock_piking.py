from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'stock.picking'

    partner_location  = fields.Char(
        string='Partner Location')

    truck_ref = fields.Char(
        string='TRUCK Number',
        required=False)

    driver_mobile= fields.Char(
        string='Driver Mobile Number',
        required=False)

class StockMove(models.Model):
    _inherit = 'stock.move.line'

    package_details = fields.Text(
        string='Package Details',
        related='product_id.Pak_details')


class AccountMove(models.Model):
    _inherit = 'account.move'

    notice = fields.Char(string='Notice')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    unit_qty = fields.Float(compute='_compute_unit_qty', string='Unit Qty')

    def _compute_unit_qty(self):
        for rec in self:
            width = rec.product_id.width
            length = rec.product_id.length
            height = rec.product_id.height

            rec.unit_qty = 0.0
            if rec.product_uom_id.equation == 'm2':
                rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or rec.quantity == 0.0 else rec.quantity / (
                        length * width)

            elif rec.product_uom_id.equation == 'm3':
                rec.unit_qty = 0.0 if length == 0.0 or width == 0.0 or height == 0.0 or rec.quantity == 0.0 else rec.quantity / (
                        length * width * height)

            elif rec.product_uom_id.equation == 'lm':
                rec.unit_qty = 0.0 if length == 0.0 or rec.quantity == 0.0 else rec.quantity / length

            elif rec.product_uom_id.equation == 'qty' or not rec.product_uom_id.equation:
                rec.unit_qty = rec.quantity


class Partner(models.Model):
    _inherit = 'res.partner'

    company_registry = fields.Char(string="Company Registry")


class Company(models.Model):
    _inherit = 'res.company'

    print_unt_qty = fields.Boolean(string="Print Unit Qty In Invoice")


class PartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    iban = fields.Char(string="IBAN")


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    Pak_details = fields.Text(
        string='Packaging Details',
        required=False)

