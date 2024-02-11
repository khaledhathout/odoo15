from odoo import models, fields, api
import base64
from io import BytesIO


class ProductionReportWizard(models.TransientModel):
    _name = 'production.report.wizard'
    _description = 'Production Report'

    from_date = fields.Datetime('From', default=fields.Datetime.now())
    to_date = fields.Datetime('To', default=fields.Datetime.now())

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': fields.Date.from_string(self.from_date),
                'to_date': fields.Date.from_string(self.to_date),
            },
        }

        return self.env.ref('smt_mrp_custom.production_report').report_action(self, data=data)

    def get_report_xlsx(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': fields.Datetime.from_string(self.from_date),
                'to_date': fields.Datetime.from_string(self.to_date),
            },
        }

        return self.env.ref('smt_mrp_custom.production_report_xlsx').report_action(self, data=data)


class ProductionReport(models.AbstractModel):
    _name = 'report.smt_mrp_custom.production_template'

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

        docs = self.env['mrp.production'].search(
            [('date_planned_start', '>=', from_date), ('date_planned_start', '<=', to_date),
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


class ProductionReportXLSX(models.AbstractModel):
    _name = 'report.smt_mrp_custom.production_template_xlsx'
    _inherit = "report.report_xlsx.abstract"
    _description = "Production XLSX Report"

    def generate_xlsx_report(self, workbook, data, partners):
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']

        report_name = "Production Report"
        sheet = workbook.add_worksheet(report_name)
        sheet.set_row(12, 25)
        header_format1 = workbook.add_format({'bold': True, 'border': 1, 'align': 'left'})
        header_format2 = workbook.add_format({'bold': True, 'border': 1, 'align': 'right'})
        header_format3 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'font_size': 20})
        header_format4 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
        header_format5 = workbook.add_format(
            {'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#ccd1d1', 'font_size': 15})
        table_header_format = workbook.add_format(
            {'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#74b40e', 'border': 1, 'text_wrap': True,
             'font_size': 10})
        table_header_format2 = workbook.add_format(
            {'bold': True, 'border': 1, 'align': 'left', 'bg_color': '#ccd1d1', 'border': 1, 'text_wrap': True})
        table_header_format3 = workbook.add_format(
            {'border': 1, 'align': 'left', 'bg_color': '#ccd1d1', 'border': 1, 'text_wrap': True})
        body_format = workbook.add_format({'align': 'left', 'border': 1})
        body_format2 = workbook.add_format({'align': 'left', 'border': 0})

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

        docs = self.env['mrp.production'].search(
            [('date_planned_start', '>=', from_date), ('date_planned_start', '<=', to_date),
             ('state', '=', 'done'), ('company_id', '=', self.env.company.id)])

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

        sheet.merge_range('H8:K9', "Production Report", header_format3)

        sheet.merge_range('G11:L11', ("From Date: " + from_date + "  To Date: " + to_date), header_format4)

        # set columns size
        sheet.set_column('A:A', 19)
        sheet.set_column('B:B', 19)
        sheet.set_column('C:C', 19)
        sheet.set_column('D:D', 19)
        sheet.set_column('E:E', 19)
        sheet.set_column('F:F', 19)
        sheet.set_column('G:G', 19)
        sheet.set_column('H:H', 19)
        sheet.set_column('I:I', 19)
        sheet.set_column('J:J', 19)
        sheet.set_column('K:K', 19)
        sheet.set_column('L:L', 19)
        sheet.set_column('M:M', 19)
        sheet.set_column('N:N', 19)
        sheet.set_column('O:O', 19)
        sheet.set_column('P:P', 19)
        sheet.set_column('Q:Q', 19)
        sheet.set_column('R:R', 19)

        sheet.merge_range(12, 0, 13, 0, "Production Order", table_header_format)
        sheet.merge_range(12, 1, 13, 1, "Operation Name", table_header_format)
        sheet.merge_range(12, 2, 13, 2, "Scheduled Date", table_header_format)
        sheet.merge_range(12, 3, 13, 3, "Responsible", table_header_format) # ********
        sheet.merge_range(12, 4, 13, 4, "BOM", table_header_format) # ********
        sheet.merge_range(12, 5, 13, 5, "Work Center", table_header_format)
        sheet.merge_range(12, 6, 13, 6, "Duration", table_header_format)
        sheet.merge_range(12, 7, 13, 7, "Component Location", table_header_format)
        sheet.merge_range(12, 8, 13, 8, "Finish Location", table_header_format)
        sheet.merge_range(12, 9, 12, 19, "Components", table_header_format)
        sheet.write(13, 9, "Product Name", table_header_format)
        sheet.write(13, 10, "Category", table_header_format) # ********
        sheet.write(13, 11, "Code", table_header_format)
        sheet.write(13, 12, "Length", table_header_format)
        sheet.write(13, 13, "Width", table_header_format)
        sheet.write(13, 14, "Height", table_header_format)
        sheet.write(13, 15, "QTY", table_header_format)
        sheet.write(13, 16, "QTY of Unit", table_header_format)
        sheet.write(13, 17, "UOM", table_header_format)
        sheet.write(13, 18, "Valuation Price", table_header_format)
        sheet.write(13, 19, "Serial No", table_header_format)
        sheet.merge_range(12, 20, 12, 30, "Finish Products", table_header_format)
        sheet.write(13, 20, "Product Name", table_header_format)
        sheet.write(13, 21, "Category", table_header_format)
        sheet.write(13, 22, "Code", table_header_format) # ********
        sheet.write(13, 23, "Length", table_header_format)
        sheet.write(13, 24, "Width", table_header_format)
        sheet.write(13, 25, "Height", table_header_format)
        sheet.write(13, 26, "QTY", table_header_format)
        sheet.write(13, 27, "Unit QTY", table_header_format)
        sheet.write(13, 28, "UOM", table_header_format)
        sheet.write(13, 29, "Valuation Price", table_header_format)
        sheet.write(13, 30, "Serial No", table_header_format)

        moves = self.env['stock.move.line'].search(['|', ('move_id.raw_material_production_id', 'in', docs.ids), ('move_id.production_id', 'in', docs.ids)])
        comp_row = 14
        finish_row = 14
        for doc in docs:
            col = 0
            sheet.write(comp_row, col, doc.name, body_format)
            col += 1
            sheet.write(comp_row, col, ', '.join(map(lambda x: x.name or "", doc.workorder_ids)), body_format)
            col += 1
            sheet.write(comp_row, col, str(doc.date_planned_start.strftime('%Y/%m/%d %H:%M:%S')), body_format)
            col += 1
            sheet.write(comp_row, col, doc.user_id.name, body_format)
            col += 1
            sheet.write(comp_row, col, doc.bom_id.display_name if doc.bom_id else "", body_format)
            col += 1
            sheet.write(comp_row, col, ', '.join(map(lambda x: x.workcenter_id.name or "", doc.workorder_ids)),body_format)
            col += 1
            sheet.write(comp_row, col, ', '.join(map(lambda x: str(x.duration), doc.workorder_ids)),body_format)
            col += 1
            sheet.write(comp_row, col, doc.location_src_id.name, body_format)
            col += 1
            sheet.write(comp_row, col, doc.location_dest_id.name, body_format)
            if comp_row >= finish_row:
                finish_row = comp_row
            else:
                comp_row = finish_row
            for raw in moves.filtered(lambda l: l.move_id.id in doc.move_raw_ids.mapped("id")):
                col =9
                sheet.write(comp_row, col, raw.move_id.product_id.name, body_format)
                col += 1
                sheet.write(comp_row, col, raw.move_id.product_id.categ_id.name, body_format)
                col += 1
                sheet.write(comp_row, col, raw.move_id.product_id.default_code, body_format)
                col += 1
                sheet.write(comp_row, col, raw.lot_id.length, body_format)
                col += 1
                sheet.write(comp_row, col, raw.lot_id.width, body_format)
                col += 1
                sheet.write(comp_row, col, raw.lot_id.height, body_format)
                col += 1
                sheet.write(comp_row, col, raw.qty_done, body_format)
                col += 1
                sheet.write(comp_row, col, raw.unit_qty, body_format)
                col += 1
                sheet.write(comp_row, col, raw.move_id.product_uom.name, body_format)
                col += 1
                sheet.write(comp_row, col, raw.move_id.valuation_value, body_format)
                col += 1
                sheet.write(comp_row, col, raw.lot_id.name or "", body_format)
                col += 1
                comp_row += 1

            for finish in moves.filtered(lambda l: l.move_id.id in doc.move_finished_ids.mapped("id")):
                finish_col = 20
                col = 0
                sheet.write(finish_row, col, doc.name, body_format)
                col += 1
                if doc.workorder_ids:
                    sheet.write(finish_row, col, ', '.join(map(lambda x: x.name or "", doc.workorder_ids)), body_format)
                    col += 1
                else:
                    sheet.write(finish_row, col, "", body_format)
                    col += 1
                sheet.write(finish_row, col, str(doc.date_planned_start.strftime('%Y/%m/%d %H:%M:%S')), body_format)
                col += 1
                sheet.write(finish_row, finish_col, finish.move_id.product_id.name, body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col, finish.move_id.product_id.categ_id.name, body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col, finish.move_id.product_id.default_code, body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col, finish.lot_id.length, body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col, finish.lot_id.width, body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col, finish.lot_id.height, body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col,
                            doc.product_qty if doc.production_mechanism != "multiple_lot" else sum(self.env[
                                'lot.lines'].search([('lot_producing_id', '=', finish.lot_id.id)]).mapped("product_qty")), body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col,
                            doc.unit_qty if doc.production_mechanism != "multiple_lot" else sum(self.env[
                                'lot.lines'].search([('lot_producing_id', '=', finish.lot_id.id)]).mapped("unit_qty")), body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col, finish.move_id.product_uom.name, body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col, finish.move_id.valuation_value, body_format)
                finish_col += 1
                sheet.write(finish_row, finish_col, finish.lot_id.name or "", body_format)
                finish_row += 1
