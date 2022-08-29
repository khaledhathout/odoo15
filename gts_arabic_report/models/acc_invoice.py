# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models,  _
from mako.pyparser import reserved
import base64
import codecs

from odoo.exceptions import UserError
from odoo.tools import get_lang








class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'



    def send_and_print_action(self):
        if self.is_email:
            if not self.partner_ids:
                raise UserError(_('No email selected'))
            mail_list = []
            for mail in self.partner_ids:
                mail_list.append(mail.email)
                composer_body = self.composer_id.body
            values = self.template_id.generate_email(self.res_id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
            values['body_html'] = composer_body
            name = values['attachments'][0][0]
            data = values['attachments'][0][1]

            li = list(values['email_cc'].split(","))

            for i in mail_list[:]:
                if i in li:
                    mail_list.remove(i)

            str_mail = ''
            for mstr in mail_list:
                str_mail += mstr+','
            values['email_to'] = str_mail[:-1]
            # attachment_id = self.env["ir.attachment"].create({
            #     'name': name,
            #     'type': "binary",
            #     'mimetype': "text/scss",
            #     'datas': data,
            #
            # })
            values['attachment_ids'] = self.attachment_ids

            # remove attachments key as it is not available in mail.mail object
            del values['attachments']

            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
            if self.is_print:
                return self._print_document()

            if self.env.context.get('mark_invoice_as_sent'):
                # Salesman send posted invoice, without the right to write
                # but they should have the right to change this flag
                self.mapped('invoice_ids').sudo().write({'is_move_sent': True})





class Invoice(models.Model):
    _inherit = 'account.move'

    amount_untaxed = fields.Float(compute='_compute_amount', store=True)
    amount_tax = fields.Float(compute='_compute_amount', store=True)
    amount_total = fields.Float(compute='_compute_amount', store=True)
    amount_residual = fields.Float(compute='_compute_amount', store=True)
    customer_po = fields.Char('Customer PO')
    tag_ids = fields.Many2many('crm.tag', string='Tags')
    # tag_ids = fields.Many2many('crm.tag', 'sale_order_tag_rel', 'order_id', 'tag_id', string='Tags')
    paid_date = fields.Date()
    paid_user_id = fields.Many2one('res.users', string='Paid Users')
    approved_date = fields.Datetime('Approved Date')

    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        # atr cc
        # template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
        template = self.env.ref('gts_email_send.email_template_edi_invoice1', raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)
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
            force_email=True
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

    # def write(self, vals):
    #     result = super(Invoice, self).write(vals)
    #     for record in self:
    #         if vals.get('payment_id'):
    #             print ("payment =======", record, record.payment_id, record.payment_id.reconciled_invoice_ids)
    #             record.payment_id.reconciled_invoice_ids.write({'paid_date': record.payment_id.date,
    #                           'paid_user_id': record.payment_id.write_uid.id})
    #             # record.paid_date = record.payment_id.date
    #             # record.paid_user_id = record.payment_id.write_uid.id
    #             # self._cr.execute("update account_move set paid_date = %s, paid_user_id = %s where id = %s",
    #             #                  (record.payment_id.date, record.payment_id.write_uid.id, record.id))
    #             # print ("record id=====", record.id, self.id, record.payment_id.date)
    #     return result


    # def action_invoice_sent(self):
    #     self.ensure_one()
    #     template_id = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
    #     lang = self.env.context.get('lang')
    #     template = self.env['mail.template'].browse(template_id)
    #     if template.lang:
    #         lang = template._render_lang(self.ids)[self.id]
    #     ctx = {
    #         'default_model': 'account.move',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         # 'mark_so_as_sent': True,
    #         'custom_layout': "mail.mail_notification_paynow",
    #         # 'proforma': self.env.context.get('proforma', False),
    #         'force_email': True,
    #         # 'model_description': self.with_context(lang=lang).type_name,
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(False, 'form')],
    #         'view_id': False,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    def action_post(self):
        self.approved_date = datetime.datetime.now()
        self.customer_po = self.ref
        res = super(Invoice, self).action_post()
        if self.move_type != 'entry':
            number = self.name
            # number = number.replace('/', '-')
            self.name = number
        return res

    def invoice_data_bae64_string(self):
        seller, vat, ts, invoice_total, vat_total = self.company_id.name, \
                        self.company_id.vat, self.approved_date, self.amount_total, self.amount_tax
        # Hex Conversion to all QR information
        if not vat:
            vat = ''
            # raise UserError(_('Sellers VAT Not Found'))
        seller_hex = seller.encode('utf-8').hex()
        vat_hex = vat.encode('utf-8').hex()
        ts_hex = str(ts).encode('utf-8').hex()
        invoice_total_hex = str(invoice_total).encode('utf-8').hex()
        vat_total_hex = str(vat_total).encode('utf-8').hex()
        # Name Length Hex values
        seller_len_hex = hex(len(seller))
        vat_len_hex = hex(len(vat))
        ts_len_hex = hex(len(str(ts)))
        invoice_total_len_hex = hex(len(str(invoice_total)))
        vat_total_len_hex = hex(len(str(vat_total)))

        seller_len_hex = seller_len_hex.replace('x', '') if len(seller_len_hex) == 3 \
            else seller_len_hex.replace('0x', '')
        vat_len_hex = vat_len_hex.replace('x', '') if len(vat_len_hex) == 3 \
            else vat_len_hex.replace('0x', '')
        if len(ts_len_hex) == 3:
            ts_len_hex = ts_len_hex.replace('x', '')
        else:
            ts_len_hex = ts_len_hex.replace('0x', '')
        if len(invoice_total_len_hex) == 3:
            invoice_total_len_hex = invoice_total_len_hex.replace('x', '')
        else:
            invoice_total_len_hex = invoice_total_len_hex.replace('0x', '')
        if len(vat_total_len_hex) == 3:
            vat_total_len_hex = vat_total_len_hex.replace('x', '')
        else:
            vat_total_len_hex = vat_total_len_hex.replace('0x', '')

        # Concatination of all hex converted variables
        hex_string = "01" + seller_len_hex + seller_hex + \
                     "02" + vat_len_hex + vat_hex + \
                     "03" + ts_len_hex + ts_hex + \
                     "04" + invoice_total_len_hex + invoice_total_hex + \
                     "05" + vat_total_len_hex + vat_total_hex
        string_base64 = codecs.encode(codecs.decode(hex_string, 'hex'), 'base64').decode()
        return string_base64

    # def report_data(self):
    #     vals = {}
    #     res = self._get_reconciled_info_JSON_values()
    #     for rec in res:
    #         if rec.get('date') and rec.get('account_payment_id'):
    #             account = self.env['account.payment'].browse(rec.get('account_payment_id'))
    #             vals.update({'paid_date': rec.get('date'), 'paid_user_id': account.write_uid.id})
    #     return vals

#     @api.multi
#     def get_late_data(self):
#         if not self.employee_ids:
#             hr_employee = self.env['hr.attendance'].sudo().search([('is_late','=',True),('company_id', '=', self.company_id.id)])
#         else:
#             hr_employee = self.env['hr.attendance'].search([('employee_id','in',self.employee_ids.ids),('is_late','=',True),('employee_id.company_id','=',self.company_id.id)])
#         return hr_employee

    # @api.model
    # def create(self, values):
    #     res = super(Invoice, self).create(values)
    #     if res:
    #         product_id = self.env.ref('arabic_report.discount_product_template')
    #         account_id = self.env.ref('arabic_report.discount_account_account')
    #
    #         if res.journal_id:
    #             if res.type in ('out_invoice', 'in_refund'):
    #                 account_id = res.journal_id.default_credit_account_id
    #             else:
    #                 account_id = res.journal.default_debit_account_id
    #         if res.invoice_line_ids.filtered(lambda r: r.discount > 0) and product_id and account_id:
    #
    #             total_discount = (res.price_unit * quantity) - res.price_subtotal
    #
    #             values = {
    #                 'origin': res.origin,
    #                 'product_id': product_id.id,
    #                 'price_unit': -total_discount,
    #                 'invoice_id': res.id,
    #                 'account_id': account_id.id,
    #                 'name': "Discount",
    #                 'custom_sequence': product_id.product_tmpl_id.custom_sequence,
    #                 'active': False,
    #                 'invoice_line_tax_ids':False,
    #             }
    #             self.env['account.invoice.line'].create(values)
    #     return res

    # @api.model
    # def invoice_line_move_line_get(self):
    #     res = []
    #
    #     invoice_line_ids = self.env['account.invoice.line'].with_context(active_test=False).search([('invoice_id', '=', self.id)])
    #
    #     for line in invoice_line_ids:
    #         if line.quantity==0:
    #             continue
    #         tax_ids = []
    #         for tax in line.invoice_line_tax_ids:
    #             tax_ids.append((4, tax.id, None))
    #             for child in tax.children_tax_ids:
    #                 if child.type_tax_use != 'none':
    #                     tax_ids.append((4, child.id, None))
    #         analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
    #
    #         move_line_dict = {
    #             'invl_id': line.id,
    #             'type': 'src',
    #             'name': line.name.split('\n')[0][:64],
    #             'price_unit': line.price_unit,
    #             'quantity': line.quantity,
    #             'price': line.price_subtotal,
    #             'account_id': line.account_id.id,
    #             'product_id': line.product_id.id,
    #             'uom_id': line.uom_id.id,
    #             'account_analytic_id': line.account_analytic_id.id,
    #             'tax_ids': tax_ids,
    #             'invoice_id': self.id,
    #             'analytic_tag_ids': analytic_tag_ids
    #         }
    #         if line['account_analytic_id']:
    #             move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
    #         res.append(move_line_dict)
    #     return res


class InvoiceLine(models.Model):
    _inherit = 'account.move.line'

    line_amount_tax = fields.Float(compute="_compute_price", store=True)
    line_amount_taxed = fields.Float(compute="_compute_price", store=True)
    # price_subtotal = fields.Float(compute="_compute_price", store=True)

    @api.depends(
        'price_unit', 'discount', 'tax_ids', 'quantity',
        'product_id', 'move_id.partner_id', 'move_id.currency_id', 'move_id.company_id',
        'move_id.invoice_date', 'move_id.date')
    def _compute_price(self):
        # super(InvoiceLine, self)._compute_price()
        for record in self:
            currency = record.move_id and record.move_id.currency_id or None
            price = record.price_unit * (1 - (record.discount or 0.0) / 100.0)
            taxes = {}
            if record.tax_ids:
                taxes = record.tax_ids.compute_all(price, currency, record.quantity, product=record.product_id,
                                                   partner=record.move_id.partner_id)
                record.line_amount_tax = taxes['total_included'] - taxes['total_excluded']
            record.line_amount_taxed = record.line_amount_tax + record.price_subtotal


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        if self._context.get("active_model") == 'account.move':
            for act_id in self._context.get('active_ids',[]):
                move_id = self.env['account.move'].search([('id','=', act_id)])
                move_id.write({
                    'paid_date': self.payment_date,
                    'paid_user_id': self.env.user.id,
                })
        payments = self._create_payments()

        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action
