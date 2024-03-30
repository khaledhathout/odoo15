import json
import logging

import requests
import werkzeug
from odoo import http, api, SUPERUSER_ID, _
from odoo import registry as registry_get
from odoo.addons.auth_oauth.controllers.main import OAuthLogin, OAuthController, fragment_to_query_string
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo.addons.web.controllers.main import set_cookie_and_redirect, login_and_redirect, ensure_db
from odoo.exceptions import AccessDenied
from odoo.http import request
from werkzeug.exceptions import BadRequest

_logger = logging.getLogger(__name__)


class KsOAuthLoginHome(Home):
    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return request.redirect(request.params.get('redirect'))
        providers = self.list_providers()

        response = super(OAuthLogin, self).web_login(*args, **kw)
        if response.is_qweb:
            error = request.params.get('oauth_error')
            if error == '1':
                error = _("Sign up is not allowed on this database.")
            elif error == '2':
                error = _("Access Denied")
            elif error == '3':
                error = _(
                    "Email Already Exist please contact your administrator.")
            elif error == '4':
                error = _(
                    "Validation End Point either Not present or invalid, Please contact your Administrator")
            elif error == '5':
                error = _(
                    "Github Oauth Api Calling Failed, For more information from system logs please contact Admisitrator")
            elif error == '6':
                error = _(
                "Github Oauth Api Calling Failed,Client ID or Client Secret Not present or has been compromised For more information from system logs please contact Admisitrator")
            else:
                error = None

            response.qcontext['providers'] = providers
            if error:
                response.qcontext['error'] = error

        return response


class KsOAuthController(OAuthController):

    @http.route('/ks/auth_oauth/signin', type='http', auth='none')
    @fragment_to_query_string
    def ks_signin(self, **kw):
        state = json.loads(kw['state'])
        user_data = json.loads((kw['user_data']))
        dbname = state['d']
        if not http.db_filter([dbname]):
            return BadRequest()
        provider = state['p']
        context = state.get('c', {})
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, context)
                validation = {
                    'user_id': user_data.get('github_id'),
                    'email': user_data.get('email') or user_data.get('username'),
                    'name': user_data.get('github_name') or user_data.get("username"),
                }
                login = env['res.users'].sudo()._auth_oauth_signin(provider, validation, kw)
                user = env['res.users'].sudo().search([('login', '=', login)])
                user.write({'git_username': user_data.get('username'),
                            'git_email': user_data.get("email")})
                credentials = (request.env.cr.dbname, login, kw.get('access_token'))
                cr.commit()
                action = state.get('a')
                menu = state.get('m')
                redirect = werkzeug.urls.url_unquote_plus(state['r']) if state.get('r') else False
                url = '/web'
                if redirect:
                    url = redirect
                elif action:
                    url = '/web#action=%s' % action
                elif menu:
                    url = '/web#menu_id=%s' % menu
                resp = login_and_redirect(*credentials, redirect_url=url)
                # Since /web is hardcoded, verify user has right to land on it
                return resp
            except AttributeError:
                # auth_signup is not installed
                _logger.error("auth_signup not installed on database %s: oauth sign up cancelled." % (dbname,))
                url = "/web/login?oauth_error=1"
            except AccessDenied:
                # oauth credentials not valid, user could be on a temporary session
                _logger.info(
                    'OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies')
                url = "/web/login?oauth_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception as e:
                # signup error
                _logger.exception("OAuth2: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return set_cookie_and_redirect(url)


class KsOAuthLogin(OAuthLogin):

    def list_providers(self):
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        except Exception:
            providers = []
        for provider in providers:
            state = self.get_state(provider)
            if provider.get('name') in ['GitHub', 'github']:
                params = dict(
                    client_id=provider['client_id'],
                    scope=provider['scope'],
                    state=json.dumps(state),
                )
                provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.urls.url_encode(params))
            else:
                return_url = request.httprequest.url_root + 'auth_oauth/signin'
                params = dict(
                    response_type='token',
                    client_id=provider['client_id'],
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    state=json.dumps(state),
                )
                provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.urls.url_encode(params))
        return providers


class KsCallbackHandler(http.Controller):

    @http.route(['/oauth/callback'], auth='public', csrf=False, methods=['GET', 'POST'], type='http')
    def get_oauth_token(self, **post):
        if post.get('state'):
            provider = request.env['auth.oauth.provider'].sudo().browse(json.loads(post.get('state')).get('p'))
        else:
            provider = request.env.ref('ks_github_auth_oauth.provider_github')
            provider = request.env[provider._name].sudo().browse(provider.id)
        redirect_url = request.httprequest.url_root + "ks/auth_oauth/signin"
        if post.get("code"):
            client_id = provider.client_id
            client_secret = provider.ks_client_secret
            if not client_id or not client_secret:
                r_url = "/web/login?oauth_error=6"
                _logger.info(
                    'OAuth2: Either of Client ID or Client Secret not present, access denied, redirect to main page in case a valid session exists, without setting cookies')
                redirect = werkzeug.utils.redirect(r_url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": post.get("code")
            }
            url = provider.validation_endpoint  # "https://github.com/login/oauth/access_token"
            if "oauth" not in url:
                r_url = "/web/login?oauth_error=4"
                _logger.info(
                    'OAuth2: Validation Endpoint not presesnt, access denied, redirect to main page in case a valid session exists, without setting cookies')
                redirect = werkzeug.utils.redirect(r_url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            response = requests.post(url, json=data)
            if response.status_code in [200, 201] and response.reason == 'OK':
                response_data = response.content.decode("UTF-8").split('&')
                if 'error=' in response_data or 'error=' in response_data[0]:
                    r_url = "/web/login?oauth_error=5"
                    _logger.info(
                        'OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies. REASON :- %s'% str(
                        response_data[0]))
                    redirect = werkzeug.utils.redirect(r_url, 303)
                    redirect.autocorrect_location_header = False
                    return redirect
                auth_token = response_data[0].split('=')[1]
                user_data = requests.get('https://api.github.com/user', auth=('', auth_token)).json()
                params = {
                    'username': user_data.get('login'),
                    'github_id': user_data.get('id'),
                    'github_name': user_data.get('name'),
                    'email': user_data.get('email'),
                }
                redirect_url = redirect_url + '?access_token=%s&state=%s&user_data=%s&provider=%s' % (
                    auth_token, post.get('state'), json.dumps(params), provider.id)
                return werkzeug.utils.redirect(redirect_url)
