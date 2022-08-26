import logging
import requests
import json
from odoo import fields, models, _
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class WhatsappTemplates(models.Model):
    _name = 'whatsapp.templates'
    _description = "Template"
    _rec_name = "name"

    def _get_default(self):
        language_id = self.env['res.lang'].search([('code', '=', 'en_US')])
        return language_id.id

    name = fields.Char(string='Name')
    languages = fields.Many2one('res.lang', string='Languages', default=_get_default)
    category = fields.Char(string='Category')
    header = fields.Selection([('text', 'Text'), ('media_image', 'Media:Image'), ('media_document', 'Media:Document'), ('media_video', 'Media:Video'), ('location', 'Location')],
                              default="text", string='Header')
    body = fields.Text(string='Body')
    state = fields.Selection([('draft', 'Draft'), ('post', 'Posted')], string="State", default="draft", required=True)
    namespace = fields.Char(string='Namespace')
    sample_url = fields.Char(string="Header Url")
    sample_message = fields.Text(string="Sample Message")
    header_text = fields.Char(string="Header Text")
    template_type = fields.Selection(
        [('simple', 'Simple Template'), ('add_sign', 'Add Signature'), ('add_chatter_msg', 'Add Chater Message'), ('add_order_product_details', 'Add Product Details'),
         ('add_order_info', 'Add Order infor')], string="Template Type", default="add_sign", required=True)
    footer = fields.Text(string="Footer")
    approval_state = fields.Char(string="Approval State")
    interactive_actions = fields.Selection([('none', 'None'), ('call_to_action', 'Call To Action'), ('quick_replies', 'Quick Replies')], default='none',
                                           string='Interactive Actions')
    whatsapp_call_to_action_ids = fields.One2many('whatsapp.template.call.to.action', 'whatsapp_template_id', string='Call To Action')
    template_id = fields.Char(string='Template Id')
    provider = fields.Selection([('whatsapp_chat_api', 'Whatsapp Chat Api'), ('gupshup', 'Gupshup')], string="Provider")
    default_template = fields.Boolean(string='Default Template')
    quick_reply1 = fields.Char(string='Quick Reply1')
    quick_reply2 = fields.Char(string='Quick Reply2')
    quick_reply3 = fields.Char(string='Quick Reply3')
    send_template = fields.Boolean(string='Send Template')
    model_id = fields.Many2one('ir.model', 'Applies to', help="The type of document this template can be used with")
    whatsapp_instance_id = fields.Many2one('whatsapp.instance', string='Whatsapp instance', ondelete='restrict')

    def unlink(self):
        # If template is deleted from odoo it will deleted from respective provider
        for record in self:
            if record.provider == 'whatsapp_chat_api' and record.state == 'post':
                url = record.whatsapp_instance_id.whatsapp_endpoint + '/removeTemplate?token=' + record.whatsapp_instance_id.whatsapp_token
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, data=json.dumps({'name': record.name}), headers=headers)
                if response.status_code == 200 or response.status_code == 201:
                    _logger.info("\nDeleted %s template from whatsapp chat api" % str(record.name))
            elif record.provider == 'gupshup':
                pass
        return super(WhatsappTemplates, self).unlink()

    def import_template_from_chat_api(self):
        # Import templates from chat api if name is exists in odoo then it will add its approval state & namespace
        response = requests.get(self.whatsapp_instance_id.whatsapp_endpoint + '/templates?token=' + self.whatsapp_instance_id.whatsapp_token,
                                headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            for template in response.json()['templates']:
                if template['name'] == self.name:
                    self.namespace = template['namespace']
                    self.approval_state = template.get('status')
                    if template.get('status') == 'approved':
                        self.state = 'post'

    def import_template_from_gupshup(self):
        # Import templates from gupshup if name is exists in odoo then it will add its id,approval state & corresponding details
        return True

    def action_import_template(self):
        # Select provider & import templates
        if self.provider == 'whatsapp_chat_api':
            self.import_template_from_chat_api()
        elif self.provider == 'gupshup':
            self.import_template_from_gupshup()

    def action_export_template_to_chat_api(self):
        # Export template on chat api
        template_data = {"category": self.category}
        if self.sample_message:
            if self.header == 'media_image':
                separate_content = self.sample_message.split(",")
                template_data.update({
                    "components": [
                        {
                            "example": {"header_handle": ["https://www.pragtech.co.in/pdf/whatsapp/pos_receipt.jpg"]},
                            "format": "IMAGE",
                            "type": "HEADER"
                        },
                        {
                            "example": {"body_text": [separate_content]},
                            "text": self.body,
                            "type": "BODY"
                        }
                    ],
                })

            elif self.header == 'media_video':
                separate_content = self.sample_message.split(",")
                template_data.update({
                    "components": [
                        {
                            "example": {"header_handle": ["https://www.pragtech.co.in/pdf/whatsapp/pragmatic_core_values.mp4"]},
                            "format": "VIDEO",
                            "type": "HEADER"
                        },
                        {
                            "example": {"body_text": [separate_content]},
                            "text": self.body,
                            "type": "BODY"
                        }
                    ],
                })
            elif self.header == 'media_document':
                separate_content = self.sample_message.split(",")
                template_data.update({
                    "components": [
                        {
                            "example": {"header_handle": [self.sample_url]},
                            "format": "DOCUMENT",
                            "type": "HEADER"
                        },
                        {
                            "example": {"body_text": [separate_content]},
                            "text": self.body,
                            "type": "BODY"
                        }
                    ],
                })
            elif self.header == 'text':
                if self.header_text:
                    template_data.update({
                        "components": [
                            {
                                "format": "TEXT",
                                "text": self.header_text,
                                "type": "HEADER"
                            },
                            {
                                "text": self.body,
                                "type": "BODY"
                            }
                        ],
                    })
                else:
                    template_data.update({
                        "components": [
                            {
                                "text": self.body,
                                "type": "BODY"
                            }
                        ],
                    })
        else:
            template_data.update({
                "components": [
                    {
                        "example": {"header_handle": [self.sample_url]},
                        "format": "DOCUMENT",
                        "type": "HEADER"
                    },
                    {
                        "example": {
                            "body_text": [[]]
                        },
                        "text": self.body,
                        "type": "BODY"
                    }
                ],
            })
        template_data.update({"language": self.languages.iso_code, "name": self.name})
        if self.quick_reply1:
            template_data.get('components').append({"buttons": [{'text': self.quick_reply1, 'type': 'QUICK_REPLY'}], "type": "BUTTONS"})
        if self.footer:
            template_data.get('components').append({"text": self.footer, "type": "FOOTER"})
        url = f"{self.whatsapp_instance_id.whatsapp_endpoint}{'/addTemplate'}?token={self.whatsapp_instance_id.whatsapp_token}"
        headers = {'Content-type': 'application/json'}
        add_template_response = requests.post(url, data=json.dumps(template_data), headers=headers)
        if add_template_response.status_code == 201 or add_template_response.status_code == 200:
            json_add_template_response = add_template_response.json()
            if not json_add_template_response.get('message') and not json_add_template_response.get('error'):
                _logger.info("\nAdd templates successfully in chat api add_template_response from whatsapp templates form view %s" % str(json_add_template_response))
                self.state = "post"
                if json_add_template_response.get('status'):
                    if json_add_template_response.get('status') == 'submitted' and json_add_template_response.get('namespace'):
                        self.namespace = json_add_template_response['namespace']
                    self.approval_state = json_add_template_response['status']
            else:
                if json_add_template_response and json_add_template_response.get('message'):
                    raise UserError(_("'%s'", str(json_add_template_response.get('message'))))
        else:
            if add_template_response.text:
                json_add_template_response = add_template_response.json()
                if json_add_template_response and json_add_template_response.get('message'):
                    raise UserError(_("'%s'", str(json_add_template_response.get('message'))))

    def action_export_template_to_gupshup(self):
        # Export template on gupshup
        return True

    def action_export_template(self):
        # Export template if template have signature then open wizard & add current instance signature else export templates
        if self.send_template:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Message',
                'res_model': 'export.template.wizard',
                'view_mode': 'form',
                'view_id': self.env['ir.model.data']._xmlid_to_res_id('pragtech_whatsapp_base.export_template_wizard_form'),
                'target': 'new',
                'nodestroy': True,
            }
        else:
            self.confirm_export_template()

    def confirm_export_template(self):
        # Select provider & export templates
        if self.env.context.get('active_model') and self.env.context.get('active_id'):
            record = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))
            if record.provider == 'whatsapp_chat_api':
                record.action_export_template_to_chat_api()
            elif record.provider == 'gupshup':
                record.action_export_template_to_gupshup()
        else:
            if self.provider == 'whatsapp_chat_api':
                self.action_export_template_to_chat_api()
            elif self.provider == 'gupshup':
                self.action_export_template_to_gupshup()
