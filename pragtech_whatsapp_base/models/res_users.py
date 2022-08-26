from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Users(models.Model):
    _inherit = "res.users"

    whatsapp_instance_id = fields.Many2one('whatsapp.instance', string='Whatsapp instance', help="From this instance message is sent on whatsapp")
