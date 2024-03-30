import logging

import requests
import werkzeug
from odoo import models, fields, api, _
from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.tools.misc import ustr

_logger = logging.getLogger(__name__)


class KsResUserInherit(models.Model):
    _inherit = 'res.users'

    oauth_token = fields.Char(string="Oauth Token", readonly=True)
    git_username = fields.Char(string="Git Username", default="No username")
    git_email = fields.Char(string="Github Email")

    def github_api_hit(self):
        provider = self.env.ref('ks_github_auth_oauth.provider_github')
        provider = self.env[provider._name].sudo().browse(provider.id)
        if provider:
            if not provider.client_id:
                r_url = "/web/login?oauth_error=6"
                _logger.info(
                    'OAuth2: Either of Client ID or Client Secret not present, access denied, redirect to main page in case a valid session exists, without setting cookies')
                redirect = werkzeug.utils.redirect(r_url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            url = "https://github.com/login/oauth/authorize?client_id=%s&scope=repo,user" % provider.client_id
            response = requests.get(url)
            if response.status_code in [200, 201]:
                return response.url

    @api.model
    def _signup_create_user(self, values):
        """ signup a new user using the template user """

        # check that uninvited users may sign up
        provider = self.env.ref('ks_github_auth_oauth.provider_github')
        if provider.id == values.get('oauth_provider_id') and provider.ks_user_type == 'internal':
            if 'partner_id' not in values:
                if self._get_signup_invitation_scope() != 'b2c':
                    raise SignupError(_('Signup is not allowed for uninvited users'))
            return self._create_user_from_default_template(values)
        else:
            return super(KsResUserInherit, self)._signup_create_user(values)

    def _create_user_from_default_template(self, values):
        template_user = self.env.ref('base.default_user')
        if not template_user.exists():
            raise ValueError(_('Signup: invalid template user'))
        if not values.get('login'):
            raise ValueError(_('Signup: no login given for new user'))
        if not values.get('partner_id') and not values.get('name'):
            raise ValueError(_('Signup: no name or partner given for new user'))

        # create a copy of the template user (attached to a specific partner_id if given)
        values['active'] = True
        try:
            with self.env.cr.savepoint():
                return template_user.with_context(no_reset_password=True).copy(values)
        except Exception as e:
            # copy may failed if asked login is not available.
            raise SignupError(ustr(e))
