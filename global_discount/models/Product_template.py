from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    # _inherit = "account.invoice"
    """ changing the model to account.move """
    _inherit = "product.template"

    global_discount = fields.Boolean(string="Global Discount")
