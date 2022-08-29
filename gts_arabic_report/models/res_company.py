from odoo import api, fields, models, tools, _
import base64
import os

class res_company(models.Model):
    _inherit = "res.company"


    def _get_report_logo(self):

      # return base64.b64encode(open(os.path.join(tools.config['root_path'], 'addons', 'base', 'res', 'res_company_logo.png'), 'rb') .read())
        return base64.b64encode(
                    open(os.path.join(tools.config['root_path'], 'addons', 'base', 'static', 'img', 'res_company_logo.png'),
                         'rb').read())
    website_logo = fields.Binary(default=_get_report_logo, string="Website Logo")
