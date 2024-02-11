# -*- coding: utf-8 -*-
# from odoo import http


# class /opt/odoo/workspace/albassam/smtStockCustom(http.Controller):
#     @http.route('//opt/odoo/workspace/albassam/smt_stock_custom//opt/odoo/workspace/albassam/smt_stock_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//opt/odoo/workspace/albassam/smt_stock_custom//opt/odoo/workspace/albassam/smt_stock_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('/opt/odoo/workspace/albassam/smt_stock_custom.listing', {
#             'root': '//opt/odoo/workspace/albassam/smt_stock_custom//opt/odoo/workspace/albassam/smt_stock_custom',
#             'objects': http.request.env['/opt/odoo/workspace/albassam/smt_stock_custom./opt/odoo/workspace/albassam/smt_stock_custom'].search([]),
#         })

#     @http.route('//opt/odoo/workspace/albassam/smt_stock_custom//opt/odoo/workspace/albassam/smt_stock_custom/objects/<model("/opt/odoo/workspace/albassam/smt_stock_custom./opt/odoo/workspace/albassam/smt_stock_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/opt/odoo/workspace/albassam/smt_stock_custom.object', {
#             'object': obj
#         })
