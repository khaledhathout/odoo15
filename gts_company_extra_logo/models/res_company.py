# -*- coding: utf-8 -*-

import base64
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class Company(models.Model):
    _inherit = 'res.company'


    extra_logo = fields.Binary(attachment=True, string="Additional Logo")
    pdf_watermark = fields.Binary(attachment=True, string="PDF Background Image")
    opacity = fields.Float(string="Opacity", defualt='0.5', help="The value will be from 0 to 1")
    pos_from_top = fields.Char(string="Position from top", default='300px', required=True)
    company_short_name = fields.Char(string='Company Short Name', required=True)
    # 291020211811

