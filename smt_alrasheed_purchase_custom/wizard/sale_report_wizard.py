from odoo import models, fields, api
import base64
from io import BytesIO


class SaleReportWizard(models.TransientModel):
    _name = 'sale.report.wizard'
    _description = 'Sale Report'

    from_date = fields.Date('From', default=fields.Date.today())
    to_date = fields.Date('To', default=fields.Date.today())

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': fields.Date.from_string(self.from_date),
                'to_date': fields.Date.from_string(self.to_date),
            },
        }

        return self.env.ref('smt_alrasheed_purchase_custom.sale_report').report_action(self, data=data)

    def get_report_xlsx(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': fields.Date.from_string(self.from_date),
                'to_date': fields.Date.from_string(self.to_date),
            },
        }

        return self.env.ref('smt_alrasheed_purchase_custom.sale_report_xlsx').report_action(self, data=data)


class SaleReport(models.AbstractModel):
    _name = 'report.smt_alrasheed_purchase_custom.sale_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']

        company_ar_name = self.env.company.arabic_name
        company_name = self.env.company.name
        logo = self.env.company.logo
        company_web = self.env.company.website
        company_email = self.env.company.email
        company_phone = self.env.company.phone
        company_mobile = self.env.company.mobile
        company_cr = self.env.company.company_registry
        street = self.env.company.street
        ar_street = self.env.company.arabic_street
        state = self.env.company.state_id.name
        vat = self.env.company.vat
        ar_state = self.env.company.arabic_state
        country = self.env.company.country_id.name
        ar_country = self.env.company.arabic_country

        docs = self.env['sale.order.line'].search(
            [('order_id.date_order', '>=', from_date), ('order_id.date_order', '<=', to_date),
             ('order_id.state', 'in', ['sale', 'done']), ('order_id.company_id', '=', self.env.company.id)])

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'company_ar_name': company_ar_name,
            'company_name': company_name,
            'logo': logo,
            'company_web': company_web,
            'company_email': company_email,
            'company_phone': company_phone,
            'company_mobile': company_mobile,
            'company_cr': company_cr,
            'street': street,
            'ar_street': ar_street,
            'state': state,
            'vat': vat,
            'ar_state': ar_state,
            'country': country,
            'ar_country': ar_country,
            'from_date': from_date,
            'to_date': to_date,
            'docs': docs,
        }


class SaleReportXLSX(models.AbstractModel):
    _name = 'report.smt_alrasheed_purchase_custom.sale_template_xlsx'
    _inherit = "report.report_xlsx.abstract"
    _description = "Sale XLSX Report"

    def generate_xlsx_report(self, workbook, data, partners):
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']

        report_name = "Sale Report"
        sheet = workbook.add_worksheet(report_name)
        sheet.set_row(12, 25)
        header_format1 = workbook.add_format({'bold': True, 'border': 0, 'align': 'left'})
        header_format2 = workbook.add_format({'bold': True, 'border': 0, 'align': 'right'})
        header_format3 = workbook.add_format({'bold': True, 'border': 0, 'align': 'center', 'font_size': 20})
        header_format4 = workbook.add_format({'bold': True, 'border': 0, 'align': 'center'})
        table_header_format = workbook.add_format(
            {'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#74b40e', 'border': 1, 'text_wrap': True,
             'font_size': 10})
        body_format = workbook.add_format({'align': 'left'})
        serial_format = workbook.add_format({'align': 'Center'})

        company_ar_name = self.env.company.arabic_name
        company_name = self.env.company.name
        logo = BytesIO(base64.b64decode(self.env.company.logo))
        company_web = self.env.company.website if self.env.company.website else ""
        company_email = self.env.company.email if self.env.company.email else ""
        company_phone = self.env.company.phone if self.env.company.phone else ""
        company_mobile = self.env.company.mobile if self.env.company.mobile else ""
        company_cr = self.env.company.company_registry if self.env.company.company_registry else ""
        street = self.env.company.street if self.env.company.street else ""
        ar_street = self.env.company.arabic_street if self.env.company.arabic_street else ""
        state = self.env.company.state_id.name if self.env.company.state_id else ""
        vat = self.env.company.vat if self.env.company.zip else ""
        ar_state = self.env.company.arabic_state if self.env.company.arabic_state else ""
        country = self.env.company.country_id.name if self.env.company.country_id else ""
        ar_country = self.env.company.arabic_country if self.env.company.arabic_country else ""

        docs = self.env['sale.order.line'].search(
            [('order_id.date_order', '>=', from_date), ('order_id.date_order', '<=', to_date),
             ('order_id.state', 'in', ['sale', 'done']), ('order_id.company_id', '=', self.env.company.id)])

        sheet.merge_range('A1:H2', company_name, header_format1)
        sheet.merge_range('A3:H3', ("Website: " + company_web), header_format1)
        sheet.merge_range('A4:H4', ("E-mail : " + company_email), header_format1)
        sheet.merge_range('A5:H5', ("C.r    : " + company_cr), header_format1)
        sheet.merge_range('A6:H6', ("Address: " + street + state + country), header_format1)
        sheet.insert_image('I1', "image.png",
                           {'image_data': logo, "x_offset": 0.0, "y_offset": 0.0, 'x_scale': .107, 'y_scale': 0.1})
        sheet.merge_range('K1:R2', company_ar_name, header_format2)
        sheet.merge_range('K3:R3', ("تلفون  : " + company_phone), header_format2)
        sheet.merge_range('K4:R4', ("موبايل : " + company_mobile), header_format2)
        sheet.merge_range('K5:R5', ("الضريبي: " + vat), header_format2)
        sheet.merge_range('K6:R6', ("العنوان: " + ar_street + ar_state + ar_country), header_format2)

        sheet.merge_range('H8:K9', ("مبيعات اﻷصناف حسب رقم الصنف"), header_format3)

        sheet.merge_range('G11:L11', ("من التاريخ: " + from_date + "  إلى التاريخ: " + to_date), header_format4)

        # set columns size
        sheet.set_column('B:B', 17)
        sheet.set_column('C:C', 17)
        sheet.set_column('D:D', 17)
        sheet.set_column('E:E', 17)
        sheet.set_column('F:F', 17)
        sheet.set_column('G:G', 17)
        sheet.set_column('H:H', 17)
        sheet.set_column('I:I', 17)
        sheet.set_column('J:J', 17)
        sheet.set_column('K:K', 17)
        sheet.set_column('L:L', 17)
        sheet.set_column('M:M', 17)
        sheet.set_column('N:N', 17)
        sheet.set_column('O:O', 17)
        sheet.set_column('P:P', 17)
        sheet.set_column('Q:Q', 17)
        sheet.set_column('R:R', 17)
        sheet.set_column('S:S', 17)
        sheet.set_column('T:T', 17)
        sheet.set_column('U:U', 17)
        sheet.set_column('V:V', 17)
        sheet.set_column('W:W', 17)
        sheet.set_column('X:X', 17)
        sheet.set_column('Y:Y', 17)
        sheet.set_column('Z:Z', 17)
        sheet.set_column('AA:AA', 17)
        sheet.set_column('AB:AB', 17)
        sheet.set_column('AC:AC', 17)
        sheet.set_column('AD:AD', 17)
        sheet.set_column('AE:AE', 17)
        sheet.set_column('AF:AF', 17)
        sheet.set_column('AG:AG', 17)
        sheet.set_column('AH:AH', 17)
        sheet.set_column('AI:AI', 17)
        sheet.set_column('AJ:AJ', 17)
        sheet.set_column('AK:AK', 17)
        sheet.set_column('AL:AL', 17)
        sheet.set_column('AM:AM', 17)
        sheet.set_column('AN:AN', 17)

        sheet.write(12, 0, "متسلسل", table_header_format)
        sheet.write(12, 1, "أمر البيع", table_header_format)
        sheet.write(12, 2, "حالة امر البيع", table_header_format)
        sheet.write(12, 3, "رقم الفاتورة", table_header_format)
        sheet.write(12, 4, "رقم الحساب", table_header_format)
        sheet.write(12, 5, "رقم اﻹستلام", table_header_format)
        sheet.write(12, 6, "رقم السيارة", table_header_format)
        sheet.write(12, 7, "حالة الفاتورة", table_header_format)
        sheet.write(12, 8, "تاريخ أمر البيع", table_header_format)
        sheet.write(12, 9, "تاريخ الفاتورة", table_header_format)
        sheet.write(12, 10, "اسم المندوب", table_header_format)
        sheet.write(12, 11, "فريق المبيعات", table_header_format)
        sheet.write(12, 12, "اسم العميل", table_header_format)
        sheet.write(12, 13, "مرجع العميل", table_header_format)
        sheet.write(12, 14, "الكاتوقري", table_header_format)
        sheet.write(12, 15, "المخزن المصدر", table_header_format)
        sheet.write(12, 16, "رقم الصنف", table_header_format)
        sheet.write(12, 17, "إسم الصنف", table_header_format)
        sheet.write(12, 18, "الطول", table_header_format)
        sheet.write(12, 19, "العرض", table_header_format)
        sheet.write(12, 20, "اﻹرتفاع", table_header_format)
        sheet.write(12, 21, "متر طولي", table_header_format)
        sheet.write(12, 22, "متر مربع", table_header_format)
        sheet.write(12, 23, "الكمية بالوحدة الجديدة", table_header_format)
        sheet.write(12, 24, "وحدة القياس", table_header_format)
        sheet.write(12, 25, "الكمية المطلوبة", table_header_format)
        sheet.write(12, 26, "الكية المسلمة", table_header_format)
        sheet.write(12, 27, "الكمية المفوترة", table_header_format)
        sheet.write(12, 28, "اللوت", table_header_format)
        sheet.write(12, 29, "السعر", table_header_format)
        sheet.write(12, 30, "قيمة امر البيع قبل الخصم", table_header_format)
        sheet.write(12, 31, "قيمة خصم امر البيع", table_header_format)
        sheet.write(12, 32, "صافي امر البيع بعد الخصم", table_header_format)
        sheet.write(12, 33, "قيمة ضريبة أمر البيع", table_header_format)
        sheet.write(12, 34, "إجمالي مبلغ أمر البيع", table_header_format)
        sheet.write(12, 35, "قيمة الفاتورة قبل الخصم", table_header_format)
        sheet.write(12, 36, "قيمة خصم الفاتورة", table_header_format)
        sheet.write(12, 37, "صافي الفاتورة بعد الخصم", table_header_format)
        sheet.write(12, 38, "قيمة ضريبة الفاتورة", table_header_format)
        sheet.write(12, 39, "إجمالي مبلغ الفاتورة", table_header_format)

        index = 1
        row = 13
        for doc in docs:
            col = 0
            sheet.write(row, col, index, serial_format)
            col += 1
            sheet.write(row, col, doc.order_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.order_id.state, body_format)
            col += 1
            sheet.write(row, col, doc.invoice_lines[0].move_id.name if doc.invoice_lines else '', body_format)
            col += 1
            sheet.write(row, col, doc.invoice_lines[0].account_id.name if doc.invoice_lines else "", body_format)
            col += 1
            sheet.write(row, col, doc.order_id.picking_ids[0].name if doc.order_id.picking_ids else '', body_format)
            col += 1
            if doc.order_id.picking_ids:
                sheet.write(row, col,
                            doc.order_id.picking_ids[0].truck_ref if doc.order_id.picking_ids[0].truck_ref else '',
                            serial_format)
            else:
                sheet.write(row, col, "", serial_format)
            col += 1
            sheet.write(row, col, doc.get_invoice_state(), body_format)
            col += 1
            sheet.write(row, col, str(doc.order_id.date_order.strftime('%Y/%m/%d')), body_format)
            col += 1
            if doc.invoice_lines:
                sheet.write(row, col, str(doc.invoice_lines[0].move_id.invoice_date.strftime('%Y/%m/%d')) if doc.invoice_lines[0].move_id.invoice_date else "", body_format)
            else:
                sheet.write(row, col, "", body_format)
            col += 1
            sheet.write(row, col, doc.order_id.user_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.order_id.team_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.order_id.partner_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.order_id.client_order_ref, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.categ_id.name, body_format)
            col += 1
            if doc.move_ids:
                sheet.write(row, col, doc.move_ids[0].picking_id.location_id.name, body_format)
            else:
                sheet.write(row, col, "", body_format)
            col += 1
            sheet.write(row, col, doc.product_id.default_code, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.length, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.width, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.height, body_format)
            col += 1
            sheet.write(row, col, (doc.product_id.length * doc.unit_qty), body_format)
            col += 1
            sheet.write(row, col, (doc.product_id.length * doc.product_id.width * doc.unit_qty),
                        body_format)
            col += 1
            sheet.write(row, col, doc.unit_qty, body_format)
            col += 1
            sheet.write(row, col, doc.product_uom.name, body_format)
            col += 1
            sheet.write(row, col, doc.product_uom_qty, body_format)
            col += 1
            sheet.write(row, col, doc.qty_delivered, body_format)
            col += 1
            sheet.write(row, col, doc.qty_invoiced, body_format)
            col += 1
            if doc.move_ids:
                for move in doc.move_ids:
                    sheet.write(row, col, ', '.join(map(lambda x: x.name or "", move.lot_ids)), body_format)
            else:
                sheet.write(row, col, "", body_format)
            col += 1
            sheet.write(row, col, doc.price_unit, body_format)
            col += 1
            sheet.write(row, col, (doc.price_unit * doc.product_uom_qty), body_format)
            col += 1
            sheet.write(row, col, round(doc.price_unit * doc.product_uom_qty, 2) - doc.price_subtotal, body_format)
            col += 1
            sheet.write(row, col, doc.price_subtotal, body_format)
            col += 1
            sheet.write(row, col, doc.price_tax, body_format)
            col += 1
            sheet.write(row, col, (doc.price_subtotal + doc.price_tax), body_format)
            col += 1
            sheet.write(row, col, (doc.invoice_lines[0].price_unit * doc.invoice_lines[0].quantity) if doc.invoice_lines else "", body_format)
            col += 1
            sheet.write(row, col, (round(doc.invoice_lines[0].price_unit * doc.invoice_lines[0].quantity, 2) - doc.invoice_lines[0].price_subtotal) if doc.invoice_lines else "", body_format)
            col += 1
            sheet.write(row, col, doc.invoice_lines[0].price_subtotal if doc.invoice_lines else "", body_format)
            col += 1
            sheet.write(row, col, (sum((doc.invoice_lines[0].price_subtotal * tax.amount) for tax in doc.invoice_lines[0].tax_ids) / 100) if doc.invoice_lines else "", body_format)
            col += 1
            sheet.write(row, col, (round(doc.invoice_lines[0].price_subtotal, 2) + (sum(round(doc.invoice_lines[0].price_subtotal * tax.amount, 2) for tax in doc.invoice_lines[0].tax_ids) / 100)) if doc.invoice_lines else "", body_format)
            index += 1
            row += 1
