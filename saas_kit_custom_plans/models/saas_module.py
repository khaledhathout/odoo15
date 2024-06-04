# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError, Warning
from . lib import module_lib

import logging

_logger = logging.getLogger(__name__)

class SaasModule(models.Model):
    _inherit = 'saas.module'


    @api.depends('name')
    def set_default_path(self):
        for obj in self:
            IrDefault = obj.env['ir.default'].sudo()
            addons_path = IrDefault.get('res.config.settings', 'addons_path')
            obj.addons_path = addons_path

    is_published = fields.Boolean(string="Publised", default=False)
    price = fields.Integer(string="Price")
    auto_install = fields.Boolean(string="Auto Install Module", default=True)
    addons_path = fields.Char(string="Addons Path", compute="set_default_path", store=True, readonly=False)
    order_line_id = fields.Many2one(comodel_name="sale.order.line")
    contract_id = fields.Many2one(comodel_name="saas.contract")
    odoo_version_id = fields.Many2one(comodel_name="saas.odoo.version")

    @api.constrains('odoo_version_id')
    def check_name_and_version(self):
        check=self.env['saas.module'].sudo().search([('technical_name','=',self.technical_name), ('id','!=',self.id), ('odoo_version_id','=',self.odoo_version_id.id)])
        if (check):
            raise UserError("Module with same version already exists!")

    def check_available_version(self):
        IrDefault = self.env['ir.default'].sudo()
        is_odoo_version = IrDefault.get('res.config.settings', 'is_odoo_version')
        domain = []
        if not is_odoo_version:
            domain = [('code', '=', '15.0')]
        domain.append(('state', '=', 'confirm'))
        version = self.env['saas.odoo.version'].sudo().search(domain)
        return version and True or False
            
        
    def toggle_module_publish(self):
        if not self.is_published:
            """
            Check whether the module exist in the path or not.
            """
            if not self.check_available_version():
                raise UserError("No Version has been configured yet, please configure atleast one version to continue")
            if self.auto_install:
                res = module_lib.check_if_module([self.addons_path], self.technical_name)
                if res.get('status'):
                    self.is_published = not self.is_published                  
                elif not res.get('msg'):
                    raise UserError("You have Selected Auto install for the Module but Module does not present on the Defautl path.")
                else:
                    raise UserError(res.get('msg'))
            else:
                self.is_published = not self.is_published
        else:
            self.is_published = not self.is_published


