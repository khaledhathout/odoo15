from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    type = fields.Selection(
        selection_add=[('view', 'View')],
        ondelete={'view': 'set default'}
    )
    internal_group = fields.Selection(
        selection_add=[('view', 'View')],
        ondelete={'view': lambda recs: recs.write({'internal_group': 'off_balance'})}
    )


class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"
    _parent_name = "parent_id"
    _parent_store = True

    parent_id = fields.Many2one(
        comodel_name='account.account.template',
        domain=[('internal_type', '=', 'view')]
    )
    parent_path = fields.Char(
        index=True
    )


class AccountAccount(models.Model):
    _inherit = "account.account"
    _parent_name = "parent_id"
    _parent_store = True

    parent_id = fields.Many2one(
        comodel_name='account.account',
        domain=[('internal_type', '=', 'view')]
    )
    parent_path = fields.Char(
        index=True
    )
    child_ids = fields.One2many(
        'account.account', 'parent_id', 'Child Accounts'
    )

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args is None and [] or args
        if not self.env.context.get('show_view'):
            domain += [('internal_type', '!=', 'view')]
        return super(AccountAccount, self)._name_search(name, domain, operator ,limit ,name_get_uid)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is None:
            domain = []
        if not self.env.context.get('show_view'):
            domain += [('internal_type', '!=', 'view')]
        return super(AccountAccount, self).search_read(domain, fields, offset, limit, order)

    @api.constrains('internal_type')
    def contains_journal_items(self):
        for rec in self:
            if rec.internal_type == 'view' and rec.env['account.move.line'].search([('account_id', '=', rec.id)], limit=1):
                raise UserError(_('You cannot set view type on an account that contains journal items.'))


