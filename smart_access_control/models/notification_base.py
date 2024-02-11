from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class NotificationBase(models.Model):
    _name = 'notification.base'
    _description = 'Notification'

    name = fields.Char('Name')
    model_ids = fields.Many2many('ir.model', compute="get_model_ids", string="Model")
    active = fields.Boolean(string="Active")
    line_ids = fields.One2many('base.line', 'base_id', string='line', copy=True)
    company_id = fields.Many2one('res.company', string='Company')

    def get_model_ids(self):
        for rec in self :
            rec.model_ids = rec.line_ids.sudo().mapped('model_id').ids

    def write(self,vals):
        self.env.cache.invalidate()
        return super(NotificationBase, self).write(vals)


class BaseLine(models.Model):
    _name = 'base.line'
    _description = 'Base Line'

    base_id = fields.Many2one('notification.base', string='Base')
    model_id = fields.Many2one('ir.model', string="Model",ondelete='cascade')
    type = fields.Selection([
        ('create', 'Create'),
        ('read', 'Read'),
        ('write', 'Write'),
        ('unlink', 'Unlink'),
    ], string='Type')
    user_ids = fields.Many2many('res.users', string='User')

class OverrideAccessWrite(models.Model):
    _inherit = "ir.model.access"

    @api.model
    @tools.ormcache_context('self.env.uid', 'self.env.su', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        if model in ['res.users', 'ir.model','base.line']:
            return super(OverrideAccessWrite, self).check(model, mode, raise_exception)
        try:
             lines = self.env['base.line'].sudo().search(
                    [('base_id','!=',False)])
        except:
             return super(OverrideAccessWrite, self).check(model, mode, raise_exception)
        lines = lines.filtered(lambda x: x.type == mode and x.model_id.model == model and self.env.user  not in x.user_ids)

        if  lines and model in lines.mapped('model_id.model'):
                return False
        else:
                return super(OverrideAccessWrite, self).check(model, mode, raise_exception)

    

class IrModel(models.Model):
    _inherit = 'ir.model'

    def name_get(self):
        result = []
        for res in self:
            name = str(res.name)  + ' / ' + str(res.model)
            result.append((res.id, name))
        return result
