from odoo import fields, models, api
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.setu_advance_inventory_reports.library import xlsxwriter
from . import setu_excel_formatter
import base64
from io import BytesIO
from .exc_quary import create_get_products_stock_movements_sp
from .exc_quary import create_get_stock_data_sp
from .exc_quary import create_opening_stock_sp

class SetuStockMovementReport(models.TransientModel):
    _name = "setu.stock.movement.report"
    _description = """
        Stock movement report is used to capture all the transactions of products between 
        specific time frame.
        
        Report will be downloaded in excel file, following data will be exported to excel file.
        -   Product
        -   Product Category
        -   Warehouse 
        -   Company
        -   Opening Stock
        -   Purchase
        -   Sales
        -   Purchase Return
        -   Sales Return
        -   Internal Transfer In
        -   Internal Transfer Out
        -   Inventory Adjustment In
        -   Inventory Adjustment Out
        -   Stock To Transit (Transit IN)
        -   Transit To Stock (Transit Out)
        -   Production IN
        -   Production Out
        -   Closing Stock
    """

    get_report_from_beginning = fields.Boolean("Report up to a certain date?")
    stock_file_data = fields.Binary('Stock Movement File')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    upto_date = fields.Date("Inventory movements up to a certain date")
    company_ids = fields.Many2many("res.company", string="Companies")
    product_category_ids = fields.Many2many("product.category", string="Product Categories")
    product_ids = fields.Many2many("product.product", string="Products")
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouses")
    # location_ids = fields.Many2many("stock.location", string="Locations")


    @api.onchange('product_category_ids')
    def onchange_product_category_id(self):
        if self.product_category_ids:
            return {'domain' : { 'product_ids' : [('categ_id','child_of', self.product_category_ids.ids)] }}

    @api.onchange('company_ids')
    def onchange_company_id(self):
        if self.company_ids:
            return {'domain' : { 'warehouse_ids' : [('company_id','child_of', self.company_ids.ids)] }}

    def get_report_date_range(self):
        if self.get_report_from_beginning:
            start_date = '1900-01-01'
            end_date = self.upto_date.strftime("%Y-%m-%d")
            return start_date, end_date
        else:
            start_date = self.start_date and self.start_date.strftime("%Y-%m-%d") or '1900-01-01'
            end_date = self.end_date and self.end_date.strftime("%Y-%m-%d")
            return start_date, end_date

    def get_product_stock_movements(self):
        """
            This method is used to get all stock transactions according to the filters
            which has been selected by users.
        :return: This methods returns List of dictionaries in which following data will be there
        -   Company
        -   Product
        -   Product Category
        -   Warehouse
        -   Opening Stock
        -   Purchase
        -   Sales
        -   Purchase Return
        -   Sales Return
        -   Internal Transfer In
        -   Internal Transfer Out
        -   Inventory Adjustment In
        -   Inventory Adjustment Out
        -   Stock To Transit (Transit IN)
        -   Transit To Stock (Transit Out)
        -   Production IN
        -   Production Out
        -   Closing Stock
        """

        # If user choose to get report up to a certain data then
        # start date should be pass null and
        # end date should be the selected date

        start_date, end_date = self.get_report_date_range()

        category_ids = company_ids = {}
        if self.product_category_ids:
            categories = self.env['product.category'].search([('id','child_of',self.product_category_ids.ids)])
            category_ids = set(categories.ids) or {}
        products = self.product_ids and set(self.product_ids.ids) or {}

        if self.company_ids:
            companies = self.env['res.company'].search([('id','child_of',self.company_ids.ids)])
            company_ids = set(companies.ids) or {}
        else:
            company_ids = set(self.env.context.get('allowed_company_ids',False) or self.env.user.company_ids.ids) or {}

        warehouses = self.warehouse_ids and set(self.warehouse_ids.ids) or {}

        # get_products_stock_movements(company_ids, product_ids, category_ids, warehouse_ids, start_date, end_date)
        query = """
            Select * from get_products_stock_movements('%s','%s','%s','%s','%s','%s')
        """%(company_ids, products, category_ids, warehouses, start_date, end_date)
        print(query)
        self._cr.execute(query)
        stock_data = self._cr.dictfetchall()
        return  stock_data

    def download_report(self):
        create_get_stock_data_sp(self._cr)
        # create_opening_stock_sp(self._cr)
        create_get_products_stock_movements_sp(self._cr)
        file_name = self.get_file_name()
        file_pointer = BytesIO()
        stock_data = self.get_product_stock_movements()
        warehouse_wise_stock_data = self.prepare_data_to_write(stock_data=stock_data)
        if not warehouse_wise_stock_data:
            return False
        workbook = self.create_excel_workbook(file_pointer)

        for stock_data_key, stock_data_value in warehouse_wise_stock_data.items():
            sheet_name = stock_data_key[1]
            wb_worksheet = self.create_excel_worksheet(workbook, sheet_name)
            row_no = 4
            self.write_report_data_header(workbook, wb_worksheet, row_no)
            for movement_data_key, movement_data_value in stock_data_value.items():
                row_no = row_no + 1
                self.write_data_to_worksheet(workbook, wb_worksheet, movement_data_value, row=row_no)
        self.create_adjustment_worksheet(workbook, warehouse_wise_stock_data)

        # workbook.save(file_name)
        workbook.close()
        file_pointer.seek(0)
        file_data = base64.encodebytes(file_pointer.read())
        self.write({'stock_file_data' : file_data})
        file_pointer.close()

        return {
            'name' : 'Stock Movement Report',
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=setu.stock.movement.report&field=stock_file_data&id=%s&filename=%s'%(self.id, file_name),
            'target': 'self',
        }

    def get_file_name(self):
        filename = "stock_movement_report"
        if self.get_report_from_beginning:
            filename = filename + "_upto_" + self.upto_date.strftime("%Y-%m-%d") + ".xlsx"
        else:
            filename = filename + "_from_" + self.start_date.strftime("%Y-%m-%d") + "_to_" + self.end_date.strftime("%Y-%m-%d") + ".xlsx"
        return filename

    def prepare_data_to_write(self, stock_data={}):
        """
            Method will prepare warehouse wise stock movement for each products which are selected
            or filtered by user inputs.

            In this format data will be prepared in the dictionary
            {
               (warehouse_id, warehouse_name) :
                    {
                        product_id :
                        {
                             "company_id":1,
                             "company_name":"Setu Consulting",
                             "product_id":2,
                             "product_name":"6ft_carpet",
                             "product_category_id":4,
                             "category_name":"All / Saleable / Floor Decoration",
                             "warehouse_id":1,
                             "warehouse_name":"Setu Main Warehouse",
                             "opening_stock":0.0,
                             "sales":3.0,
                             "sales_return":2.0,
                             "purchase":10.0,
                             "purchase_return":0.0,
                             "internal_in":0.0,
                             "internal_out":1.0,
                             "adjustment_in":0.0,
                             "adjustment_out":1.0,
                             "production_in":0.0,
                             "production_out":0.0,
                             "transit_in":0.0,
                             "transit_out":0.0,
                             "closing":7.0
                        },

                    },
            }
        :param stock_data:
        :return:
        """
        warehouse_wise_data = {}
        for data in stock_data:
            key = (data.get('warehouse_id'), data.get('warehouse_name'), data.get('adjustment_valuation'))
            if not warehouse_wise_data.get(key,False):
                warehouse_wise_data[key] = {data.get('product_id') : data}
            else:
                warehouse_wise_data.get(key).update({data.get('product_id') : data})
        return warehouse_wise_data

    def create_excel_workbook(self, file_pointer):
        # self.start_date.strftime("%Y-%m-%d")
        # file_name = self.get_file_name()
        workbook = xlsxwriter.Workbook(file_pointer)
        return workbook

    def create_excel_worksheet(self, workbook, sheet_name):
        worksheet = workbook.add_worksheet(sheet_name)
        worksheet.set_default_row(20)
        # worksheet.set_border()
        return worksheet

    def set_column_width(self, workbook, worksheet):
        worksheet.set_column(0, 2, 20)
        worksheet.set_column(3, 16, 12)

    def set_format(self, workbook, wb_format):
        wb_new_format = workbook.add_format(wb_format)
        wb_new_format.set_border()
        return wb_new_format

    def set_report_title(self, workbook, worksheet):
        wb_format = self.set_format(workbook, setu_excel_formatter.FONT_TITLE_CENTER)
        worksheet.merge_range(0, 0, 1, 16, "Stock Movement Report", wb_format)
        start_date, end_date = self.get_report_date_range()
        wb_format_left = self.set_format(workbook, setu_excel_formatter.FONT_MEDIUM_BOLD_LEFT)
        wb_format_center = self.set_format(workbook, setu_excel_formatter.FONT_MEDIUM_BOLD_CENTER)
        report_string = ""
        if start_date == '1900-01-01':
            report_string = "Stock Movements up to"
            worksheet.merge_range(2, 0, 2, 1, report_string, wb_format_left)
            worksheet.write(2, 2, end_date, wb_format_center)
        else:
            worksheet.write(2, 0, "From Date", wb_format_left)
            worksheet.write(2, 1, start_date, wb_format_center)
            worksheet.write(3, 0, "End Date", wb_format_left)
            worksheet.write(3, 1, end_date, wb_format_center)

    def write_report_data_header(self, workbook, worksheet, row):
        self.set_report_title(workbook,worksheet)
        self.set_column_width(workbook, worksheet)

        wb_format = self.set_format(workbook, setu_excel_formatter.FONT_MEDIUM_BOLD_CENTER)
        wb_format.set_text_wrap()

        odd_normal_right_format = self.set_format(workbook, setu_excel_formatter.ODD_FONT_MEDIUM_BOLD_RIGHT)
        even_normal_right_format = self.set_format(workbook, setu_excel_formatter.EVEN_FONT_MEDIUM_BOLD_RIGHT)
        normal_left_format = self.set_format(workbook, setu_excel_formatter.FONT_MEDIUM_BOLD_LEFT)

        # company name = 1 column
        worksheet.write(row, 0, 'Company', normal_left_format)
        # product name = 2 column
        worksheet.write(row, 1, 'Product Name', normal_left_format)
        worksheet.write(row, 2, 'Product Code', normal_left_format)
        # category name = 3 column
        worksheet.write(row, 3, 'Category', normal_left_format)
        # opening stock = 4 column
        worksheet.write(row, 4, 'Opening Stock', even_normal_right_format)
        worksheet.write(row, 5, 'Valuation', odd_normal_right_format)
        # sales = 5 column
        worksheet.write(row, 6, 'Sales', even_normal_right_format)
        worksheet.write(row, 7, 'Valuation', odd_normal_right_format)
        # sales_return = 6 column
        worksheet.write(row, 8, 'Sales Return', even_normal_right_format)
        worksheet.write(row, 9, 'Valuation', odd_normal_right_format)
        # purchase = 7 column
        worksheet.write(row, 10, 'Purchase', even_normal_right_format)
        worksheet.write(row, 11, 'Valuation', odd_normal_right_format)
        # purchase_return = 8 column
        worksheet.write(row, 12, 'Purchase Return', even_normal_right_format)
        worksheet.write(row, 13, 'Valuation', odd_normal_right_format)
        # internal_in = 9 column
        worksheet.write(row, 14, 'Internal IN', even_normal_right_format)
        worksheet.write(row, 15, 'Valuation', odd_normal_right_format)
        # internal_out = 10 column
        worksheet.write(row, 16, 'Internal OUT', even_normal_right_format)
        worksheet.write(row, 17, 'Valuation', odd_normal_right_format)
        # adjustment_in = 11 column
        worksheet.write(row, 18, 'Adjustment IN', even_normal_right_format)
        worksheet.write(row, 19, 'Valuation', odd_normal_right_format)
        # adjustment_out = 12 column
        worksheet.write(row, 20, 'Adjustment OUT', even_normal_right_format)
        worksheet.write(row, 21, 'Valuation', odd_normal_right_format)
        # production_in = 13 column
        worksheet.write(row, 22, 'Production IN', even_normal_right_format)
        worksheet.write(row, 23, 'Valuation', odd_normal_right_format)
        # production_out = 14 column
        worksheet.write(row, 24, 'Production OUT', even_normal_right_format)
        worksheet.write(row, 25, 'Valuation', odd_normal_right_format)
        # transit_in = 15 column
        worksheet.write(row, 26, 'Transit IN', even_normal_right_format)
        worksheet.write(row, 27, 'Valuation', odd_normal_right_format)
        # transit_out = 16 column
        worksheet.write(row, 28, 'Transit OUT', even_normal_right_format)
        worksheet.write(row, 29, 'Valuation', odd_normal_right_format)
        # closing = 17 column
        worksheet.write(row, 30, 'Total Valuation', even_normal_right_format)
        # closing = 16 column
        worksheet.write(row, 31, 'Closing', odd_normal_right_format)
        

        return worksheet

    def write_data_to_worksheet(self, workbook, worksheet, data, row):
        # Start from the first cell. Rows and
        # columns are zero indexed.
        odd_normal_right_format = self.set_format(workbook, setu_excel_formatter.ODD_FONT_MEDIUM_NORMAL_RIGHT)
        even_normal_right_format = self.set_format(workbook, setu_excel_formatter.EVEN_FONT_MEDIUM_NORMAL_RIGHT)
        normal_left_format = self.set_format(workbook, setu_excel_formatter.FONT_MEDIUM_NORMAL_LEFT)

        product_id = self.env['product.product'].search([('id','=',data.get('product_id',''))])
        standard_price = product_id.standard_price
        total_valuations = data.get('opening_stock_valuation','') + data.get('sales_valuation','') + data.get('purchase_valuation','') +  data.get('purchase_return_valuation','') + data.get('internal_in_valuation','') + data.get('internal_out_valuation','') + data.get('adjustment_in_valuation','') + data.get('adjustment_out_valuation','') + data.get('production_in_valuation','') + data.get('transit_in_valuation','') + data.get('transit_out_valuation','')

        # company name = 1 column
        worksheet.write(row, 0, data.get('company_name',''), normal_left_format)
        # product name = 2 column
        worksheet.write(row, 1, data.get('product_name',''), normal_left_format)
        worksheet.write(row, 2, data.get('product_code',''), normal_left_format)
        # category name = 3 column
        worksheet.write(row, 3, data.get('category_name',''), normal_left_format)
        # opening stock = 4 column
        worksheet.write(row, 4, data.get('opening_stock',''), even_normal_right_format)
        worksheet.write(row, 5, data.get('opening_stock_valuation',''), odd_normal_right_format)
        # sales = 5 column
        worksheet.write(row, 6, data.get('sales',''), even_normal_right_format)
        worksheet.write(row, 7, data.get('sales_valuation',''), odd_normal_right_format)
        # sales_return = 6 column
        worksheet.write(row, 8, data.get('sales_return',''), even_normal_right_format)
        worksheet.write(row, 9, data.get('sales_return_valuation',''), odd_normal_right_format)
        # purchase = 7 column
        worksheet.write(row, 10, data.get('purchase',''), even_normal_right_format)
        worksheet.write(row, 11, data.get('purchase_valuation',''), odd_normal_right_format)
        # purchase_return = 8 column
        worksheet.write(row, 12, data.get('purchase_return',''), even_normal_right_format)
        worksheet.write(row, 13, data.get('purchase_return_valuation',''), odd_normal_right_format)
        # internal_in = 9 column
        worksheet.write(row, 14, data.get('internal_in',''), even_normal_right_format)
        worksheet.write(row, 15, data.get('internal_in_valuation',''), odd_normal_right_format)
        # internal_out = 10 column
        worksheet.write(row, 16, data.get('internal_out',''), even_normal_right_format)
        worksheet.write(row, 17, data.get('internal_out_valuation',''), odd_normal_right_format)
        # adjustment_in = 11 column
        worksheet.write(row, 18, data.get('adjustment_in',''), even_normal_right_format)
        worksheet.write(row, 19, data.get('adjustment_in_valuation',''), odd_normal_right_format)
        # adjustment_out = 12 column
        worksheet.write(row, 20, data.get('adjustment_out',''), even_normal_right_format)
        worksheet.write(row, 21, data.get('adjustment_out_valuation',''), odd_normal_right_format)
        # production_in = 13 column
        worksheet.write(row, 22, data.get('production_in',''), even_normal_right_format)
        worksheet.write(row, 23, data.get('production_in_valuation',''), odd_normal_right_format)
        # production_out = 14 column
        worksheet.write(row, 24, data.get('production_out',''), even_normal_right_format)
        worksheet.write(row, 25, data.get('production_out_valuation',''), odd_normal_right_format)
        # transit_in = 15 column
        worksheet.write(row, 26, data.get('transit_in',''), even_normal_right_format)
        worksheet.write(row, 27, data.get('transit_in_valuation',''), odd_normal_right_format)
        # transit_out = 16 column
        worksheet.write(row, 28, data.get('transit_out',''), even_normal_right_format)
        worksheet.write(row, 29, data.get('transit_out_valuation',''), odd_normal_right_format)
        # closing = 17 column
        worksheet.write(row, 30, total_valuations, even_normal_right_format)
        # closing = 16 column
        worksheet.write(row, 31, data.get('closing',''), odd_normal_right_format)
        

    def create_adjustment_worksheet(self, workbook, data):
        sheet = workbook.add_worksheet('Adjustment')
        sheet.set_column(0, 2, 20)
        sheet.set_column(3, 16, 12)
        odd_normal_right_format = self.set_format(workbook, setu_excel_formatter.ODD_FONT_MEDIUM_NORMAL_RIGHT)
        even_normal_right_format = self.set_format(workbook, setu_excel_formatter.EVEN_FONT_MEDIUM_NORMAL_RIGHT)

        total_closing = 0
        total_valuation_move = 0
        total_valuation_adjustment =0
        
        for stock_data_key, stock_data_value in data.items():
            for movement_data_key, movement_data_value in stock_data_value.items():
                total_closing += movement_data_value.get('closing','')
                total_valuation_adjustment = movement_data_value.get('adjustment_valuation','') or 0
                total_valuation = movement_data_value.get('opening_stock_valuation','') + movement_data_value.get('sales_valuation','') +  movement_data_value.get('purchase_valuation','') +  movement_data_value.get('purchase_return_valuation','') +  movement_data_value.get('internal_in_valuation','') + movement_data_value.get('internal_out_valuation','') + movement_data_value.get('adjustment_in_valuation','') + movement_data_value.get('adjustment_out_valuation','') + movement_data_value.get('production_in_valuation','') + movement_data_value.get('transit_in_valuation','') + movement_data_value.get('transit_out_valuation','')
                total_valuation_move += total_valuation

        sheet.write(5, 1, 'Final Closing', odd_normal_right_format)
        sheet.write(6, 1, 'Final Adjustment Valuation', odd_normal_right_format)
        sheet.write(7, 1, 'Final Movement Valuation', odd_normal_right_format)
        sheet.write(8, 1, 'Final Valuation', odd_normal_right_format)

        sheet.write(5, 2, total_closing, even_normal_right_format)
        sheet.write(6, 2, total_valuation_adjustment, even_normal_right_format)
        sheet.write(7, 2, total_valuation_move, even_normal_right_format)
        sheet.write(8, 2, total_valuation_adjustment + total_valuation_move, even_normal_right_format)
