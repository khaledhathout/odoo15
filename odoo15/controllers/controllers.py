# -*- coding: utf-8 -*-
# from odoo import http


# class Odoo15(http.Controller):
#     @http.route('/odoo15/odoo15', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo15/odoo15/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo15.listing', {
#             'root': '/odoo15/odoo15',
#             'objects': http.request.env['odoo15.odoo15'].search([]),
#         })

#     @http.route('/odoo15/odoo15/objects/<model("odoo15.odoo15"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo15.object', {
#             'object': obj
#         })
