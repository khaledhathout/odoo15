# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import tempfile
from odoo.tools.misc import xlwt
import io
import base64
import time
from dateutil.relativedelta import relativedelta
from pytz import timezone


class Inventory_Turnover_analysis_wizard(models.Model):
    _name = 'inventory.turnover.report.wiz'
    _description = 'Warehouse Turnover Analysis Report'

    from_date = fields.Date('Start Date')
    to_date = fields.Date('End Date')
    company_ids = fields.Many2many("res.company", string="Companies")
    category_ids = fields.Many2many("product.category", string="Product Categories")
    product_ids = fields.Many2many("product.product", string="Products")
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouses")

    def print_inventory_turnover_report(self):

        filename = 'Warehouse Turnover Analysis Report' + '.xls'
        workbook = xlwt.Workbook()

        worksheet = workbook.add_sheet('Warehouse Turnover Analysis Report')
        font = xlwt.Font()
        font.bold = True
        for_left = xlwt.easyxf(
            "font: bold 1, color black; borders: top double, bottom double, left double, right double; align: horiz left")
        for_left_not_bold = xlwt.easyxf("font: color black; align: horiz left", num_format_str='0.00')

        GREEN_TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name Tahoma, height 250;'
            'align: vertical center, horizontal center, wrap on;'
            'borders: top double, bottom double, left double, right double;'
        )
        style = xlwt.easyxf(
            'font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')

        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '0.00'

        worksheet.row(0).height = 500
        worksheet.col(0).width = 10000
        worksheet.col(1).width = 7000
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 4000
        worksheet.col(4).width = 4000
        worksheet.col(5).width = 4000
        worksheet.col(6).width = 4000
        worksheet.col(7).width = 4000

        worksheet.write_merge(0, 0, 0, 5, 'Warehouse Turnover Analysis Report', GREEN_TABLE_HEADER)

        row = 2

        col = 0
        worksheet.write(row, col, 'Company' or '', for_left)
        col += 1
        company = ', '.join(self.company_ids.mapped('name')) if self.company_ids else ''
        worksheet.write(row, col, company, for_left_not_bold)
        row += 1

        col = 0
        worksheet.write(row, col, 'Warehouse' or '', for_left)
        col += 1
        warehouse = ', '.join(self.warehouse_ids.mapped('name')) if self.warehouse_ids else ''
        worksheet.write(row, col, warehouse, for_left_not_bold)
        row += 1

        row += 1
        worksheet.write(row, 0, 'Report start date' or '', for_left)
        worksheet.write(row, 1, self.from_date.strftime('%d-%m-%Y') or '', for_left)
        row += 1
        worksheet.write(row, 0, 'Report end date' or '', for_left)
        worksheet.write(row, 1, self.to_date.strftime('%d-%m-%Y') or '', for_left)

        row += 1

        worksheet.write(row, 0, 'Product Name' or '', for_left)
        worksheet.write(row, 1, 'Category' or '', for_left)
        worksheet.write(row, 2, 'Opening Stock' or '', for_left)
        worksheet.write(row, 3, 'Closing Stock' or '', for_left)
        worksheet.write(row, 4, 'Average Stock' or '', for_left)
        worksheet.write(row, 5, 'Sales' or '', for_left)
        worksheet.write(row, 6, 'Turnover Ratio' or '', for_left)

        rows = row + 1

        self._create_turnover_data()
        dispaly_data = self.env['inventory.turnover.extended'].search([])
        for record in dispaly_data:
            worksheet.write(rows, 0, record.products.name_get()[0][1] or '', for_left_not_bold)
            worksheet.write(rows, 1, record.product_category.name_get()[0][1] or '', for_left_not_bold)
            worksheet.write(rows, 2, record.stock_opening or '0.0', for_left_not_bold)
            worksheet.write(rows, 3, record.stock_closing or '0.0', for_left_not_bold)
            worksheet.write(rows, 4, record.stock_average or '0.0', for_left_not_bold)
            worksheet.write(rows, 5, record.sales or '0.0', for_left_not_bold)
            worksheet.write(rows, 6, record.turnover or '0.0', for_left_not_bold)

            rows += 1

        fp = io.BytesIO()
        workbook.save(fp)

        
        turnover_id = self.env['inventory.turnover.extended'].create(
            {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': turnover_id.id,
            'res_model': 'inventory.turnover.extended',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }

    def _create_turnover_data(self):
        cr = self.env.cr
        where_clause = ""

        domain = []
        location_domain = []
        query_domain = []

        location_domain.append(('usage', 'in', ['internal']))

        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))
            location_domain.append(('company_id', 'in', self.company_ids.ids))

        location_ids = self.env['stock.location']
        warehouse = self.env['stock.warehouse'].sudo().search([], limit=1)

        if self.warehouse_ids:
            location_ids = self.warehouse_ids.mapped('lot_stock_id')
            location_ids += location_ids.mapped('child_ids')
            warehouse = self.warehouse_ids[0]

        if not location_ids:
            location_ids = self.env['stock.location'].search(location_domain)

        domain += ['|', ('location_id', 'in', location_ids.ids), ('location_dest_id', 'in', location_ids.ids)]
        domain += [('state', '=', 'done')]

        date_start = self.from_date
        date_end = self.to_date

        opening_stock_domain = domain + [('date', '<=', date_start)]

        opening_stock_data = self.env['stock.move.line'].search(opening_stock_domain)

        closing_stock_domain = domain + [('date', '>=', date_start)] + [('date', '<=', date_end)]
        closing_stock_data = self.env['stock.move.line'].search(closing_stock_domain)

        opening_qty = sum(
            opening_stock_data.filtered(lambda x: x.location_dest_id in location_ids).mapped('qty_done')) - sum(
            opening_stock_data.filtered(lambda x: x.location_id in location_ids).mapped('qty_done'))

        current_purchase_qty = sum(
            closing_stock_data.filtered(lambda x: x.location_dest_id in location_ids).mapped('qty_done'))

        if self.category_ids:
            where_clause += "AND pt.categ_id IN %s "
            query_domain.append(tuple(self.category_ids.ids))

        if self.product_ids:
            where_clause += "AND pp.id IN %s "
            query_domain.append(tuple(self.product_ids.ids))

        # Delete old data
        delete_query = """DELETE FROM inventory_turnover_extended"""
        cr.execute(delete_query)

        select_product_query = """SELECT * FROM product_template AS pt
                                    JOIN product_product AS pp ON pp.product_tmpl_id=pt.id
                                    WHERE pt.type = 'product' AND pp.active is True %s""" % where_clause
        cr.execute(select_product_query, query_domain)
        product_ids_query = cr.dictfetchall()

        for product_id in product_ids_query:

            self._cr.execute("""SELECT * FROM stock_move_line WHERE state = 'done' AND product_id = %s AND location_id in %s AND date >= %s AND date <= %s """, (product_id["id"], tuple(location_ids.ids),  date_start, date_end ))
            move_line_ids_query = self._cr.dictfetchall()

            total_sold_qty = 0
            if len(move_line_ids_query) > 0:

                total_sold_qty = sum(move['qty_done'] for move in move_line_ids_query)

            closing_qty = (opening_qty + current_purchase_qty) - total_sold_qty

            average = 0.0
            turnover = 0.0

            if opening_qty or closing_qty:
                average = (opening_qty + closing_qty) / 2

            if average:
                turnover = total_sold_qty / average

            cr.execute("""INSERT INTO inventory_turnover_extended 
            (products, product_category, company, warehouse, stock_opening, stock_closing, stock_average, sales, turnover) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (
                           product_id["id"],
                           product_id["categ_id"],
                           warehouse.company_id.id,
                           warehouse.id,
                           opening_qty,
                           closing_qty,
                           average,
                           total_sold_qty,
                           turnover)
                       )

    def tree_graph_report_view(self):
        self._create_turnover_data()
        display = []
        graph_id = self.env.ref('bi_turnover_report.inventory_turnover_extended_report_graph').id
        tree_id = self.env.ref('bi_turnover_report.inventory_turnover_extended_report_tree').id
        graph_first = self.env.context.get('report_graph', False)

        if graph_first:
            display.append((graph_id, 'graph'))
            display.append((tree_id, 'tree'))
        else:
            display.append((tree_id, 'tree'))
            display.append((graph_id, 'graph'))

        return {
            'name': _('Warehouse Turnover Ratio Analysis'),
            'res_model': 'inventory.turnover.extended',
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
            'views': display,
        }


class Inventory_Turnover_analysis_Extended(models.TransientModel):
    _name = 'inventory.turnover.extended'
    _description = "inventory turnover Excel Extended"

    excel_file = fields.Binary('Download Report :- ')
    file_name = fields.Char('Excel File', size=64)

    products = fields.Many2one("product.product", "Product")
    product_category = fields.Many2one("product.category", "Category")
    warehouse = fields.Many2one("stock.warehouse")
    company = fields.Many2one("res.company", "Company")
    stock_opening = fields.Float("Opening Stock")
    stock_closing = fields.Float("Closing Stock")
    stock_average = fields.Float("Average Stock")
    sales = fields.Float("Sales")
    turnover = fields.Float("Turnover Ratio")
    wizard_id = fields.Many2one("inventory.turnover.report.wiz")
