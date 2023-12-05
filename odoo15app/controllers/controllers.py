# -*- coding: utf-8 -*-
# from odoo import http


# class Odoo15app(http.Controller):
#     @http.route('/odoo15app/odoo15app', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo15app/odoo15app/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo15app.listing', {
#             'root': '/odoo15app/odoo15app',
#             'objects': http.request.env['odoo15app.odoo15app'].search([]),
#         })

#     @http.route('/odoo15app/odoo15app/objects/<model("odoo15app.odoo15app"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo15app.object', {
#             'object': obj
#         })
