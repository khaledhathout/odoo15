import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class KsOauthProviderInherit(models.Model):
    _inherit = "auth.oauth.provider"

    ks_client_secret = fields.Char(string="Client Secret")
    ks_is_github = fields.Boolean(compute='_compute_is_client_secret_required')
    ks_user_type = fields.Selection([('portal', 'Portal User'),
                                     ('internal', 'Internal User')], default="portal", string='User Type')

    def _compute_is_client_secret_required(self):
        for rec in self:
            if rec.auth_endpoint:
                if 'github' in rec.auth_endpoint:
                    rec.ks_is_github = True
                else:
                    rec.ks_is_github = False
            else:
                rec.ks_is_github = False
