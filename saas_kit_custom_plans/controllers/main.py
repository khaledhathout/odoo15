# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.odoo_saas_kit.controllers.main import MailController

import logging

_logger = logging.getLogger(__name__)


class CustomMailController(MailController):
    _cp_path = '/mail'

    @http.route(['/mail/confirm_domain'], type='json', auth="public", methods=['POST'], website=True)
    def confirm_domain(self, domain_name, contract_id,  **kw):
        contract = request.env['saas.contract'].sudo().browse(int(contract_id))
        if contract.is_custom_plan and not contract.server_id:
            if contract.odoo_version_id and contract.odoo_version_id.is_multi_server:
                server_res = contract.odoo_version_id.select_server()
                if server_res and server_res[0]:
                    server_id = server_res[1]
            else:    
                server_id = request.env['saas.server'].sudo().search([('state', '=', 'confirm'), ('max_clients', '>' , 'total_clients')])
            contract.server_id = server_id.id
        res = super(CustomMailController, self).confirm_domain(domain_name, contract_id, **kw)
        return res
        


class PlanPage(http.Controller):

    def _create_custom_plan_data(self, *ver):
        data = dict()
        IrDefault = request.env['ir.default'].sudo()
        version_code= ver[0] if ver else None
        data['is_odoo_version'] = IrDefault.get('res.config.settings', 'is_odoo_version')

        data['odoo_version'] = version_code if version_code else request.env['saas.odoo.version'].sudo().search([('state', '=', 'confirm')]) if data['is_odoo_version'] else request.env['saas.odoo.version'].sudo().search([('state', '=', 'confirm'), ('code', '=', '15.0')], limit=1)
        if not data['odoo_version']:
            data.clear()
            data['error'] = "Odoo Version not found."
            _logger.info("======== Error - Odoo Version not found. ==========")
            return data
        
        modules = request.env['saas.module'].sudo().search([('is_published', '=', True),('odoo_version_id.code','=',version_code if version_code else data['odoo_version'][0].code)])

        data['is_users'] = IrDefault.get('res.config.settings', 'is_users')
        data['annual_discount'] = IrDefault.get('res.config.settings', 'annual_discount')
        data['discount_percent'] = IrDefault.get('res.config.settings', 'discount_percent')
        apps_view = IrDefault.get('res.config.settings', 'apps_view')
        
        if apps_view == 'normal':
            data['normal_view'] = True
            data['categorical_view'] = False
        else:
            data['normal_view'] = False
            data['categorical_view'] = True

        data['categories'] = dict()            
        for module in modules:
            if not module.categ_id:
                if data['categories'].get('DEFAULT'):
                    data['categories']['DEFAULT'].append(module)                 
                else:
                    data['categories']['DEFAULT'] = [module]                 
            elif data['categories'].get(module.categ_id.name.upper()):
                data['categories'][module.categ_id.name.upper()].append(module)
            else:
                data['categories'][module.categ_id.name.upper()] = [module]

        data['max_users'] = IrDefault.get('res.config.settings', 'max_users')
        data['is_free_users'] = IrDefault.get('res.config.settings', 'is_free_users')
        if data['is_free_users']:
            data['free_users'] = IrDefault.get('res.config.settings', 'free_users')
            data['is_free_users'] = True if data['free_users'] else False
        else:
            data['free_users'] = 0
        data['costing_nature'] = IrDefault.get('res.config.settings', 'costing_nature')
        data['user_cost'] = IrDefault.get('res.config.settings', 'user_cost')
        if not data['is_users']:
            data['costing_nature'] = 'per_month'
        data['company'] = request.env.company
        data['modules'] = modules
        return data
    
    def _create_custom_plan_normal_data(self,version_code):
        data=dict()
        data['version_code'] = version_code
        data['modules']= request.env['saas.module'].sudo().search([('is_published', '=', True),('odoo_version_id.code','=',version_code)])
        data['company'] = request.env.company
        return data


    @http.route('/custom/plan', type='http', auth="public",  website=True)
    def custom_plan_redirect(self):
        data = self._create_custom_plan_data()
        return request.render('saas_kit_custom_plans.plan_page', data)


    @http.route('/custom/version/categ', type='json', auth="public",  website=True)
    def custom_plan_redirect_version_categ(self, version_code):
        data = self._create_custom_plan_data(version_code)
        return request.env['ir.ui.view'].sudo()._render_template('saas_kit_custom_plans.category_view_template', data)

    @http.route('/custom/version/normal', type='json', auth="public",  website=True)
    def custom_plan_redirect_version_normal(self, version_code):
        data = self._create_custom_plan_normal_data(version_code)
        return request.env['ir.ui.view'].sudo()._render_template('saas_kit_custom_plans.normal_view_template',data)


    @http.route('/saas/add/plan', type='json', auth='public', website=True)
    def saas_custom_plan_cart(self, apps=None, saas_users=None, version_name=None, total_cost=None, users_cost=None, recurring_interval=None, version_code=None , **kwargs):
        odoo_version_id = request.env['saas.odoo.version'].sudo().search([('code', '=', version_code), ('name', '=', version_name)], limit=1)        
        product_id = odoo_version_id.product_id        
        module_ids = []
        for module in apps:
            module_rec = request.env['saas.module'].sudo().search([('technical_name', '=', module), ('odoo_version_id.code', '=', odoo_version_id.code)])
            module_ids.append(module_rec.id)
        sale_order = request.website.sale_get_order(force_create=1)
        if sale_order and product_id:
            return sale_order.create_custom_contract_line(product_id=product_id, odoo_version_id=odoo_version_id, saas_users=saas_users, total_cost=total_cost, users_cost=users_cost, recurring_interval=recurring_interval, module_ids=module_ids)

    @http.route('/show/categ/view', type='http', auth='public', website=True)
    def show_categ_view(self,version_code):
        data = self._create_custom_plan_data(version_code)
        return request.render('saas_kit_custom_plans.category_view_template', data)
        
    @http.route('/show/normal/view', type='http', auth='public', website=True)
    def show_normal_view(self):
        data = self._create_custom_plan_data()
        return request.render('saas_kit_custom_plans.normal_view_template', data)

    @http.route('/show/selected/apps/view', type='http', auth='public', website=True)
    def show_selected_apps_view(self):
        data = self._create_custom_plan_data()
        return request.render('saas_kit_custom_plans.select_apps_section', data)
