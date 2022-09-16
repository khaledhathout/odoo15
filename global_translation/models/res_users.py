from odoo import models, fields


class ResUsersInherit(models.Model):
    _inherit = 'res.users'
    name = fields.Char(related='partner_id.name', inherited=True, translate=True)


class PartnerInherit(models.Model):
    _inherit = 'res.partner'
    name = fields.Char(translate=True)
