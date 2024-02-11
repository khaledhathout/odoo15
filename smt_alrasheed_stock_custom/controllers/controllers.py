# -*- coding: utf-8 -*-
# from odoo import http


# class SmtAlrasheedStockCustom(http.Controller):
#     @http.route('/smt_alrasheed_stock_custom/smt_alrasheed_stock_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smt_alrasheed_stock_custom/smt_alrasheed_stock_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smt_alrasheed_stock_custom.listing', {
#             'root': '/smt_alrasheed_stock_custom/smt_alrasheed_stock_custom',
#             'objects': http.request.env['smt_alrasheed_stock_custom.smt_alrasheed_stock_custom'].search([]),
#         })

#     @http.route('/smt_alrasheed_stock_custom/smt_alrasheed_stock_custom/objects/<model("smt_alrasheed_stock_custom.smt_alrasheed_stock_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smt_alrasheed_stock_custom.object', {
#             'object': obj
#         })
