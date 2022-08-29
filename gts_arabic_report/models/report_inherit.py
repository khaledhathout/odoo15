from odoo import api, fields, models,  _
import base64
from odoo.exceptions import UserError, AccessError


# class InvoiceReport(models.AbstractModel):
#     _name = "report.arabic_report.report_invoice_with_payments_ar"

    # def _get_report_values(self, docids, data=None):
    #     docs = self.env['account.move'].browse(docids)
    #     for invoice in docs:
    #         if invoice.state != 'posted':
    #             raise AccessError(_('You can not Generate E-Invoice for the Document which is not posted !'))
    #     return {
    #         'doc_ids': docs.ids,
    #         'doc_model': 'mrp.production',
    #         'docs': docs,
    #     }

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        rec = super(MailComposer, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        if active_model == 'account.payment':
            payments = self.env['account.payment'].search([('id', '=', self.env.context.get('active_id'))], limit=1)
            attachment_list = []
            payment_report = 'account.action_report_payment_receipt'
            template = 'account.mail_template_data_payment_receipt'
            if payments.payment_type == 'outbound':
                template = 'gts_email_send.mail_template_data_payment_payment'
            template_id = self.env.ref(template)
            data, data_format = self.env.ref(payment_report)._render_qweb_pdf(
                payments.ids)
            attach_datas = {
                'name': '%s-Receipt-%s' % (payments.company_id.company_short_name, payments.name) + '.' + data_format,
                'datas': base64.b64encode(data),
                # 'datas_fname': lines.product_id.product_tmpl_id.attach_design_pdf_filename,
                'res_model': 'mail.compose.message',
                'res_id': 0,
                'type': 'binary',
            }
            attachment = self.env['ir.attachment'].create(attach_datas)
            attachment_list.append(attachment.id)
            invoices = payments.reconciled_invoice_ids
            if payments.payment_type == 'outbound':
                invoices =  payments.reconciled_bill_ids
            for invoice in invoices:
                report_name = 'account.account_invoices'
                data, data_format = self.env.ref(report_name)._render_qweb_pdf(
                    invoice.ids)
                attach_datas = {
                    'name': '%s-VAT-Invoice-%s' % (invoice.company_id.company_short_name,invoice.name) + '.' + data_format,
                    'datas': base64.b64encode(data),
                    # 'datas_fname': lines.product_id.product_tmpl_id.attach_design_pdf_filename,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',
                }
                attachment = self.env['ir.attachment'].create(attach_datas)
                attachment_list.append(attachment.id)
            self.attachment_ids = [(6, 0, attachment_list)]
            rec.update({'attachment_ids': [(6, 0, attachment_list)],'composition_mode': 'comment',
                        'template_id': template_id.id})
        #
        return rec