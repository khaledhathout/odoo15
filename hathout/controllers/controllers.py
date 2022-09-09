# -*- coding: utf-8 -*-
# from odoo import http


# class Hathout(http.Controller):
#     @http.route('/hathout/hathout', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hathout/hathout/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hathout.listing', {
#             'root': '/hathout/hathout',
#             'objects': http.request.env['hathout.hathout'].search([]),
#         })

#     @http.route('/hathout/hathout/objects/<model("hathout.hathout"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hathout.object', {
#             'object': obj
#         })
