# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import qrcode
import base64
import io
from odoo import http
from num2words import num2words
from odoo.tools.misc import formatLang, format_date, get_lang


class AccountMove(models.Model):
    _inherit = 'account.move'

    date_due = fields.Date('Date Due')
    invoice_date_supply = fields.Date('Date Of Supply')

    def change_size_page(self, items):
        paper_format = self.env['report.paperformat'].search([('id', '=', self.env.ref('ob_saudi_vat_invoice.paperformat_action_report_tax_invoice').id)])
        
        new_size=240 + (len(items) * 5)
        paper_format.sudo().write({'page_height':new_size})


    def get_product_arabic_name(self,pid):
        translation = self.env['ir.translation'].search([
            ('name','=','product.product,name'),('state','=','translated'),
            ('res_id','=',pid)])
        if translation :
            return translation.value
        else: 
            product = self.env['product.product'].browse(int(pid))
            translation = self.env['ir.translation'].search([
                ('name','=','product.product,name'),('state','=','translated'),
                ('res_id','=',product.product_tmpl_id.id)])
            if translation :
                return translation.value
        return ''    

    def amount_word(self, amount):
        language = self.partner_id.lang or 'en'
        language_id = self.env['res.lang'].search([('code', '=', 'ar_001')])
        if language_id:
            language = language_id.iso_code
        amount_str =  str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]           
        before_amount_words = num2words(int(before_point_value),lang=language)
        after_amount_words = num2words(int(after_point_value),lang=language)
        amount = before_amount_words + ' ' + after_amount_words
        return amount

    def amount_total_words(self, amount):
        words_amount = self.currency_id.amount_to_text(amount)
        return words_amount

    @api.model
    def get_qr_code(self):

        def get_qr_encoding(tag, field):
            company_name_byte_array = field.encode('UTF-8')
            company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
            company_name_length_encoding = len(company_name_byte_array).to_bytes(length=1, byteorder='big')
            return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array

        qr_code_str = ''
        seller_name_enc = get_qr_encoding(1, self.company_id.display_name)
        company_vat_enc = get_qr_encoding(2, self.company_id.vat or '')
        time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'),self.create_date)
        timestamp_enc = get_qr_encoding(3, time_sa.isoformat())
        invoice_total_enc = get_qr_encoding(4, str(self.amount_total))
        total_vat_enc = get_qr_encoding(5, str(self.currency_id.round(self.amount_total - self.amount_untaxed)))

        str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
        qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
        return qr_code_str


    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        # template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        
        template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
        company_type = self.partner_id.company_type
        if self.move_type=='out_invoice':
            if company_type == 'person':
                template = self.env.ref('ob_saudi_vat_invoice.semail_template_edi_invoice_individual', False)
            elif company_type == 'company':
                template = self.env.ref('ob_saudi_vat_invoice.semail_template_edi_invoice_company', raise_if_not_found=False)

        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)
        print("==action_invoice_sent===1111111111")
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True,
            wizard_opened=True
        )
        return {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }



class ResPartner(models.Model):
    _inherit = 'res.partner'

    building_no = fields.Char('Building No')
    additional_no = fields.Char('Additional No')
    other_seller_id = fields.Char('Other Seller Id')


class ResCompany(models.Model):
    _inherit = 'res.company'

    building_no = fields.Char(related='partner_id.building_no', store=True, readonly=False, string='Building No')
    additional_no = fields.Char(related='partner_id.additional_no', store=True, readonly=False, string='Additional No')
    other_seller_id = fields.Char(related='partner_id.other_seller_id', store=True, readonly=False, string='Other Seller Id')
    arabic_name = fields.Char('Name')
    arabic_street = fields.Char('Street')
    arabic_street2 = fields.Char('Street2')
    arabic_city = fields.Char('City')
    arabic_state = fields.Char('State')
    arabic_country = fields.Char('Country')
    arabic_zip = fields.Char('Zip')


