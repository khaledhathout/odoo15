from odoo import models, fields, api
import base64
from io import BytesIO


class PurchaseReportWizard(models.TransientModel):
    _name = 'purchase.report.wizard'
    _description = 'Purchase Report'

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

        return self.env.ref('smt_alrasheed_purchase_custom.purchase_report').report_action(self, data=data)

    def get_report_xlsx(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': fields.Date.from_string(self.from_date),
                'to_date': fields.Date.from_string(self.to_date),
            },
        }

        return self.env.ref('smt_alrasheed_purchase_custom.purchase_report_xlsx').report_action(self, data=data)


class PurchaseReport(models.AbstractModel):
    _name = 'report.smt_alrasheed_purchase_custom.purchase_template'

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
        zip_code = self.env.company.zip
        ar_state = self.env.company.arabic_state
        country = self.env.company.country_id.name
        ar_country = self.env.company.arabic_country

        docs = self.env['purchase.order.line'].search([('date_order', '>=', from_date), ('date_order', '<=', to_date),
                                                       ('order_id.state', 'in', ['purchase', 'done']), ('company_id', '=', self.env.company.id)])

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
            'zip_code': zip_code,
            'ar_state': ar_state,
            'country': country,
            'ar_country': ar_country,
            'from_date': from_date,
            'to_date': to_date,
            'docs': docs,
        }


class PurchaseReportXLSX(models.AbstractModel):
    _name = 'report.smt_alrasheed_purchase_custom.purchase_template_xlsx'
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

        docs = self.env['purchase.order.line'].search(
            [('order_id.date_order', '>=', from_date), ('order_id.date_order', '<=', to_date),
             ('order_id.state', 'in', ['purchase', 'done']), ('company_id', '=', self.env.company.id)])

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

        sheet.merge_range('H8:K9', "Items Purchases", header_format3)

        sheet.merge_range('G11:L11', ("From Date: " + from_date + "  To Date: " + to_date), header_format4)

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

        sheet.write(12, 0, "S/No.", table_header_format)
        sheet.write(12, 1, "Purchase Order", table_header_format)
        sheet.write(12, 2, "Purchase State", table_header_format)
        sheet.write(12, 3, "Invoice Number", table_header_format)
        sheet.write(12, 4, "Account Number", table_header_format)
        sheet.write(12, 5, "Receipt No.", table_header_format)
        sheet.write(12, 6, "Truck No.", table_header_format)
        sheet.write(12, 7, "Invoice State", table_header_format)
        sheet.write(12, 8, "PO Date", table_header_format)
        sheet.write(12, 9, "Invoice Date", table_header_format)
        sheet.write(12, 10, "Supplier Name", table_header_format)
        sheet.write(12, 11, "Supplier Reference", table_header_format)
        sheet.write(12, 12, "Product Category", table_header_format)
        sheet.write(12, 13, "Destination Location", table_header_format)
        sheet.write(12, 14, "Item Name", table_header_format)
        sheet.write(12, 15, "Item Code", table_header_format)
        sheet.write(12, 16, "Length", table_header_format)
        sheet.write(12, 17, "Width", table_header_format)
        sheet.write(12, 18, "Height", table_header_format)
        sheet.write(12, 19, "Unit Qty", table_header_format)
        sheet.write(12, 20, "Product UOM", table_header_format)
        sheet.write(12, 21, "Demand QTY", table_header_format)
        sheet.write(12, 22, "Received QTY", table_header_format)
        sheet.write(12, 23, "Billed QTY", table_header_format)
        sheet.write(12, 24, "Lot", table_header_format)
        sheet.write(12, 25, "Price", table_header_format)
        sheet.write(12, 26, "Amount Before Discount", table_header_format)
        sheet.write(12, 27, "Discount Amount", table_header_format)
        sheet.write(12, 28, "Amount After Discount", table_header_format)
        sheet.write(12, 29, "Tax Amount", table_header_format)
        sheet.write(12, 30, "Total Amount", table_header_format)
        sheet.write(12, 31, "LM", table_header_format)
        sheet.write(12, 32, "M2", table_header_format)
        sheet.write(12, 33, "Purchase Responsible", table_header_format)

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
            sheet.write(row, col, doc.invoice_lines[0].move_id.name if doc.invoice_lines else "", body_format)
            col += 1
            sheet.write(row, col, doc.invoice_lines[0].account_id.name if doc.invoice_lines else "", body_format)
            col += 1
            sheet.write(row, col, doc.order_id.picking_ids[0].name if doc.order_id.picking_ids else '', body_format)
            col += 1
            if doc.order_id.picking_ids:
                sheet.write(row, col, doc.order_id.picking_ids[0].truck_ref if doc.order_id.picking_ids[0].truck_ref else '', body_format)
            else:
                sheet.write(row, col, "", body_format)
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
            sheet.write(row, col, doc.order_id.partner_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.order_id.partner_ref, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.categ_id.name, body_format)
            col += 1
            if doc.move_ids:
                sheet.write(row, col, doc.move_ids[0].picking_id.location_dest_id.name, body_format)
            else:
                sheet.write(row, col, "", body_format)
            col += 1
            sheet.write(row, col, doc.product_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.default_code, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.length, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.width, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.height, body_format)
            col += 1
            sheet.write(row, col, doc.unit_qty, body_format)
            col += 1
            sheet.write(row, col, doc.product_uom.name, body_format)
            col += 1
            sheet.write(row, col, doc.product_qty, body_format)
            col += 1
            sheet.write(row, col, doc.qty_received, body_format)
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
            sheet.write(row, col, doc.price_subtotal, body_format)
            col += 1
            sheet.write(row, col, doc.get_invoice_discount(), body_format)
            col += 1
            sheet.write(row, col, (doc.price_subtotal - doc.get_invoice_discount()), body_format)
            col += 1
            sheet.write(row, col, doc.price_tax, body_format)
            col += 1
            sheet.write(row, col, (round(doc.price_subtotal + doc.price_tax, 2) - doc.get_invoice_discount()), body_format)
            col += 1
            sheet.write(row, col, (doc.product_id.length * doc.unit_qty), body_format)
            col += 1
            sheet.write(row, col, (doc.product_id.length * doc.product_id.width * doc.unit_qty),
                        body_format)
            col += 1
            sheet.write(row, col, doc.order_id.user_id.name, body_format)
            col += 1
            index += 1
            row += 1
