from odoo import models, fields, api
import base64
from io import BytesIO


class StockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'
    _description = 'Stock Report'

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

        return self.env.ref('smt_alrasheed_stock_custom.stock_report').report_action(self, data=data)

    def get_report_xlsx(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': fields.Date.from_string(self.from_date),
                'to_date': fields.Date.from_string(self.to_date),
            },
        }

        return self.env.ref('smt_alrasheed_stock_custom.stock_report_xlsx').report_action(self, data=data)


class StockReport(models.AbstractModel):
    _name = 'report.smt_alrasheed_stock_custom.stock_template'

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

        docs = self.env['stock.move'].search([('date', '>=', from_date), ('date', '<=', to_date),
                                              ('state', '=', 'done'), ('company_id', '=', self.env.company.id)])

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


class StockReportXLSX(models.AbstractModel):
    _name = 'report.smt_alrasheed_stock_custom.stock_template_xlsx'
    _inherit = "report.report_xlsx.abstract"
    _description = "Stock XLSX Report"

    def generate_xlsx_report(self, workbook, data, partners):
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']

        report_name = "Stock Report"
        sheet = workbook.add_worksheet(report_name)
        sheet.set_row(12, 25)
        header_format1 = workbook.add_format({'bold': True, 'border': 0, 'align': 'left', 'font_name': 'Arial'})
        header_format2 = workbook.add_format({'bold': True, 'border': 0, 'align': 'right', 'font_name': 'Arial'})
        header_format3 = workbook.add_format({'bold': True, 'border': 0, 'align': 'center', 'font_size': 20, 'font_name': 'Arial'})
        header_format4 = workbook.add_format({'bold': True, 'border': 0, 'align': 'center', 'font_name': 'Arial'})
        table_header_format = workbook.add_format(
            {'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#74b40e', 'border': 1, 'text_wrap': True,
             'font_size': 10, 'font_name': 'Arial'})
        body_format = workbook.add_format({'align': 'left', 'font_name': 'Arial'})
        serial_format = workbook.add_format({'align': 'Center', 'font_name': 'Arial'})

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
        zip_code = self.env.company.zip if self.env.company.zip else ""
        ar_state = self.env.company.arabic_state if self.env.company.arabic_state else ""
        country = self.env.company.country_id.name if self.env.company.country_id else ""
        ar_country = self.env.company.arabic_country if self.env.company.arabic_country else ""

        docs = self.env['stock.move.line'].search([
            ('move_id.date', '>=', from_date), 
            ('move_id.date', '<=', to_date),
            ('move_id.state', '=', 'done'), 
            ('move_id.company_id', '=', self.env.company.id)])

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
        sheet.merge_range('K5:R5', ("ص.ب    : " + zip_code), header_format2)
        sheet.merge_range('K6:R6', ("العنوان: " + ar_street + ar_state + ar_country), header_format2)

        sheet.merge_range('H8:K9', ("Stock Moves With Details"), header_format3)

        sheet.merge_range('G11:L11', ("From Date: " + from_date + "  To Date: " + to_date), header_format4)

        # set columns size
        sheet.set_column('B:B', 14)
        sheet.set_column('C:C', 13)
        sheet.set_column('D:D', 14)
        sheet.set_column('E:E', 14)
        sheet.set_column('F:F', 13)
        sheet.set_column('G:G', 11)
        sheet.set_column('H:H', 30)
        sheet.set_column('M:M', 20)

        sheet.write(12, 0, "S/No.", table_header_format)
        sheet.write(12, 1, "Operation Type", table_header_format)
        sheet.write(12, 2, "Reference", table_header_format)
        sheet.write(12, 3, "Date", table_header_format)
        sheet.write(12, 4, "Partner", table_header_format)
        sheet.write(12, 5, "Account", table_header_format)
        sheet.write(12, 6, "Analytic Account", table_header_format)
        sheet.write(12, 7, "Warehouse", table_header_format)
        sheet.write(12, 8, "Source Location", table_header_format)
        sheet.write(12, 9, "Destination Location", table_header_format)
        sheet.write(12, 10, "Source Doc.", table_header_format)
        sheet.write(12, 11, "Responsible", table_header_format)
        sheet.write(12, 12, "Vehicle Number", table_header_format)
        sheet.write(12, 13, "Driver Name", table_header_format)
        sheet.write(12, 14, "Well Location", table_header_format)
        sheet.write(12, 15, "Well Number", table_header_format)
        sheet.write(12, 16, "Product Code", table_header_format)
        sheet.write(12, 17, "Product", table_header_format)
        sheet.write(12, 18, "Product Category", table_header_format)
        sheet.write(12, 19, "Serial No", table_header_format)
        sheet.write(12, 20, "Unit QTY", table_header_format)
        sheet.write(12, 21, "UOM", table_header_format)
        sheet.write(12, 22, "QTY", table_header_format)
        sheet.write(12, 23, "Length", table_header_format)
        sheet.write(12, 24, "Width", table_header_format)
        sheet.write(12, 25, "Height", table_header_format)
        sheet.write(12, 26, "LM", table_header_format)
        sheet.write(12, 27, "M2", table_header_format)
        sheet.write(12, 28, "Valuation Amount", table_header_format)
        sheet.write(12, 29, "Picking Reference", table_header_format)
        sheet.write(12, 30, "Note", table_header_format)

        index = 1
        row = 13
        for doc in docs:
            col = 0
            sheet.write(row, col, index, serial_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_type_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.move_id.reference, body_format)
            col += 1
            sheet.write(row, col, str(doc.move_id.date.strftime('%Y/%m/%d')), body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.partner_id.name if doc.move_id.picking_id.partner_id else '', body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.account_id.name if doc.move_id.picking_id.account_id else '', body_format)
            col += 1
            sheet.write(row, col, doc.move_id.analytic_account_id.name if doc.move_id.analytic_account_id else '', body_format)
            col += 1
            sheet.write(row, col, doc.move_id.location_dest_id.warehouse_id.name if doc.move_id.location_dest_id.warehouse_id else '', body_format)
            col += 1
            sheet.write(row, col, doc.move_id.location_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.move_id.location_dest_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.origin or "", body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.user_id.name if doc.picking_id.user_id else '', body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.vehicle_no or "", body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.driver_name or "", body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.location_well or "", body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.well_ref or "", body_format)
            col += 1
            sheet.write(row, col, doc.product_id.default_code if doc.product_id.default_code else "", body_format)
            col += 1
            sheet.write(row, col, doc.product_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.product_id.categ_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.lot_id.name, body_format)
            col += 1
            sheet.write(row, col, doc.qty_done, body_format)
            col += 1
            sheet.write(row, col, doc.move_id.product_uom.name, body_format)
            col += 1
            sheet.write(row, col, doc.product_qty, body_format)
            col += 1
            sheet.write(row, col, doc.lot_id.length, body_format)
            col += 1
            sheet.write(row, col, doc.lot_id.width, body_format)
            col += 1
            sheet.write(row, col, doc.lot_id.height, body_format)
            col += 1
            sheet.write(row, col, (doc.lot_id.length * doc.unit_qty), body_format)
            col += 1
            sheet.write(row, col, (doc.lot_id.length * doc.lot_id.width * doc.unit_qty),
                        body_format)
            col += 1
            sheet.write(row, col, abs(doc.move_id.valuation_value), body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.picking_ref or "", body_format)
            col += 1
            sheet.write(row, col, doc.move_id.picking_id.note or "", body_format)
            index += 1
            row += 1

