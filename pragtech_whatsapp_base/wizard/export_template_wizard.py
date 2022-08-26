from odoo import api, fields, models
import html2text


class ExportTemplateWizard(models.TransientModel):
    _name = 'export.template.wizard'
    _description = "Export Template Message"

    message = fields.Text(string="Response", readonly=True)
    source = fields.Selection([('instance', 'Settings'), ('template', 'Template')])
    whatsapp_instance_id = fields.Many2one('whatsapp.instance', string='Whatsapp Instance')

    @api.model
    def default_get(self, fields):
        res = super(ExportTemplateWizard, self).default_get(fields)
        res.update({
            'message': 'Make sure you have set the correct signature in WhatsApp -> Select Instance -> Signature. As once WhatsApp template is exported, WhatsApp template signature cannot change',
        })
        record = self.env[self.env.context.get('active_model','')].browse(self.env.context.get('active_id',''))
        if self.env.context.get('active_model','') == 'whatsapp.templates':
            res.update({'source': 'template', 'whatsapp_instance_id': record.whatsapp_instance_id.id})
        else:
            res.update({'source': 'instance', 'whatsapp_instance_id': record.id})
        return res

    def action_export_templates_from_wizard(self):
        whatsapp_template_ids = self.env['whatsapp.templates'].search([('send_template', '=', True), ('whatsapp_instance_id', '!=', False)])
        for whatsapp_template_id in whatsapp_template_ids:
            whatsapp_template_id.write({'footer' : whatsapp_template_id.whatsapp_instance_id.signature})
            if self.source == 'instance':
                return self.whatsapp_instance_id.confirm_export_template()
            elif self.source == 'template':
                return self.env['whatsapp.templates'].confirm_export_template()
