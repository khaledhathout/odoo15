# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class odoo15app(models.Model):
#     _name = 'odoo15app.odoo15app'
#     _description = 'odoo15app.odoo15app'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
