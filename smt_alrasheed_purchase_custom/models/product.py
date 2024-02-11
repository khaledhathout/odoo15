# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError

class Product(models.Model):
    _inherit = "product.template"

    length = fields.Float("length", digits='Dimension Decimal')
    height = fields.Float("height", digits='Dimension Decimal')
    width = fields.Float("width", digits='Dimension Decimal')

    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""",tracking=True)


class DecimalPrecision(models.Model):
    _inherit = "decimal.precision"

    is_dimension = fields.Boolean(string="Dimension")