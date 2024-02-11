# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

_logger = logging.getLogger(__name__)


class ReportStockCardReportXlsx(models.AbstractModel):
    _name = "report.stock_card_report.report_stock_card_report_xlsx"
    _description = "Stock Card Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        if objects.report_type == "with_details":
            for product in objects.product_ids:
                for ws_params in self._get_ws_params(workbook, data, product):
                    ws_name = ws_params.get("ws_name")
                    ws_name = self._check_ws_name(ws_name)
                    ws = workbook.add_worksheet(ws_name)
                    generate_ws_method = getattr(self, ws_params["generate_ws_method"])
                    generate_ws_method(workbook, ws, ws_params, data, objects, product)
        else:
            ws = workbook.add_worksheet("Stock Card Report")
            for product in objects.product_ids:
                for ws_params in self._get_ws_params(workbook, data, product):
                    generate_ws_method = getattr(self, ws_params["generate_ws_method"])
                    generate_ws_method(workbook, ws, ws_params, data, objects, product)

    def _get_ws_params(self, wb, data, product):
        filter_template = {
            "1_date_from": {
                "header": {"value": "Date from"},
                "data": {
                    "value": self._render("date_from"),
                    "format": FORMATS["format_tcell_date_center"],
                },
            },
            "2_date_to": {
                "header": {"value": "Date to"},
                "data": {
                    "value": self._render("date_to"),
                    "format": FORMATS["format_tcell_date_center"],
                },
            },
            "3_location": {
                "header": {"value": "Location"},
                "data": {
                    "value": self._render("location"),
                    "format": FORMATS["format_tcell_center"],
                },
            },
            "4_warehouse": {
                "header": {"value": "Warehouse"},
                "data": {
                    "value": self._render("warehouse"),
                    "format": FORMATS["format_tcell_center"],
                },
            },
            "5_product_category": {
                "header": {"value": "Product Category"},
                "data": {
                    "value": self._render("category"),
                    "format": FORMATS["format_tcell_center"],
                },
            },
        }

        stock_card_template = {
            "1_date": {
                "header": {"value": "Date"},
                "data": {
                    "value": self._render("date"),
                    "format": FORMATS["format_tcell_date_left"],
                },
                "width": 25,
            },
            "2_reference": {
                "header": {"value": "Reference"},
                "data": {
                    "value": self._render("reference"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 25,
            },
            "3_partner": {
                "header": {"value": "Partner"},
                "data": {
                    "value": self._render("partner"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 25,
            },
            "4_location_from": {
                "header": {"value": "Location From"},
                "data": {"value": self._render("location")},
                "width": 25,
            },
            "5_location_to": {
                "header": {"value": "Location To"},
                "data": {"value": self._render("to")},
                "width": 25,
            },
            "6_input": {
                "header": {"value": "In"},
                "data": {"value": self._render("input")},
                "width": 25,
            },
            "6_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("price_unit_in")},
                "width": 25,
            },
            "7_output": {
                "header": {"value": "Out"},
                "data": {"value": self._render("output")},
                "width": 25,
            },
            "8_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("price_unit_out")},
                "width": 25,
            },
            "9_balance": {
                "header": {"value": "Balance"},
                "data": {"value": self._render("balance")},
                "width": 25,
            },
            "9_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("price_unit")},
                "width": 25,
            },
        }

        initial_template = {
            "1_ref": {
                "data": {"value": "Initial", "format": FORMATS["format_tcell_center"]},
                "colspan": 9,
            },
            "2_balance": {
                "data": {
                    "value": self._render("balance"),
                    "format": FORMATS["format_tcell_amount_right"],
                }
            },
            "3_valuation": {
                "data": {
                    "value": self._render("valuation"),
                    "format": FORMATS["format_tcell_amount_right"],
                }
            },
        }

        totals_template = {
            "1_ref": {
                "data": {"value": "Total", "format": FORMATS["format_tcell_center_bold"]},
                "colspan": 3,
            },
            "2_ref": {
                "data": {"value": "Initial", "format": FORMATS["format_tcell_center_bold"]},
                "width": 25,
            },
            "3_initial": {
                "header": {"value": "Initial"},
                "data": {"value": self._render("initial")},
                "width": 25,
            },
            "4_total_input": {
                "header": {"value": "Total Input"},
                "data": {"value": self._render("total_input")},
                "width": 25,
            },
            "4_total_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("total_price_in")},
                "width": 25,
            },
            "5_total_output": {
                "header": {"value": "Total Output"},
                "data": {"value": self._render("total_output")},
                "width": 25,
            },
            "6_total_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("total_price_out")},
                "width": 25,
            },
            "7_total_balance": {
                "header": {"value": "Total Balance"},
                "data": {"value": self._render("total_balance")},
                "width": 25,

            },
            "8_total_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("total_price")},
                "width": 25,
            },
            "9_adjustment": {
                "header": {"value": "Adjustment"},
                "data": {"value": self._render("valuation_adjustment")},
                "width": 25,
            },

        }

        totals_template_without_details = {
            "1_product": {
                "header": {"value": "Product"},
                "data": {"value": product.name},
                "width": 25,
            },
            "2_initial_balance": {
                "header": {"value": "Initial Balance"},
                "data": {"value": self._render("balance_initial")},
                "width": 25,
            },
            "3_initial_valuation": {
                "header": {"value": "Initial Valuation"},
                "data": {"value": self._render("valuation_initial")},
                "width": 25,
            },
            "4_total_input": {
                "header": {"value": "Total Input"},
                "data": {"value": self._render("total_input")},
                "width": 25,
            },
            "5_total_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("total_price_in")},
                "width": 25,
            },
            "6_total_output": {
                "header": {"value": "Total Output"},
                "data": {"value": self._render("total_output")},
                "width": 25,
            },
            "7_total_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("total_price_out")},
                "width": 25,
            },
            "8_total_balance": {
                "header": {"value": "Total Balance"},
                "data": {"value": self._render("total_balance")},
                "width": 25,

            },
            "9_adjustment_value": {
                "header": {"value": "Valuation Adjustment"},
                "data": {"value": self._render("valuation_adjustment")},
                "width": 25,

            },
            "9_total_price": {
                "header": {"value": "Valuation Value"},
                "data": {"value": self._render("total_price")},
                "width": 25,
            },
        }

        ws_params = {
            "ws_name": product.display_name,
            "generate_ws_method": "_stock_card_report",
            "title": "Stock Card - {}".format(product.display_name),
            "wanted_list_filter": [k for k in sorted(filter_template.keys())],
            "col_specs_filter": filter_template,
            "wanted_list_initial": [k for k in sorted(initial_template.keys())],
            "col_specs_initial": initial_template,
            "wanted_list_totals": [k for k in sorted(totals_template.keys())],
            "col_specs_totals": totals_template,
            "wanted_list_totals_without_details": [k for k in sorted(totals_template_without_details.keys())],
            "col_specs_totals_without_details": totals_template_without_details,
            "wanted_list": [k for k in sorted(stock_card_template.keys())],
            "col_specs": stock_card_template,
        }
        return [ws_params]

    def _stock_card_report(self, wb, ws, ws_params, data, objects, product):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])
        self._set_column_width(ws, ws_params)
        # Title
        row_pos = 0
        if objects.report_type == "with_details":
            row_pos = self._write_ws_title(ws, row_pos, ws_params, True)

        # Filter Table
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_blue_center"],
            col_specs="col_specs_filter",
            wanted_list="wanted_list_filter",
        )
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={
                "date_from": objects.date_from or "",
                "date_to": objects.date_to or "",
                "location": ', '.join(map(lambda x: x.display_name or '', objects.location_id)),
                "warehouse": objects.warehouse_id.display_name or "",
                "category": objects.category_id.display_name or "",
            },
            col_specs="col_specs_filter",
            wanted_list="wanted_list_filter",
        )
        row_pos += 1



        if objects.report_type == "with_details":
            # Stock Card Table
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="header",
                default_format=FORMATS["format_theader_blue_center"],
            )
            ws.freeze_panes(row_pos, 0)
            balance = objects._get_initial(
                objects.results.filtered(lambda l: l.product_id == product and l.is_initial)
            )
            valuation_initial = sum(objects.results.filtered(lambda l: l.product_id == product and l.is_initial).mapped("price_unit"))
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="data",
                render_space={"balance": balance, "valuation": valuation_initial},
                col_specs="col_specs_initial",
                wanted_list="wanted_list_initial",
            )

            product_lines = objects.results.filtered(
                lambda l: l.product_id == product and not l.is_initial
            )

            filter_result = objects.results.filtered(lambda l: l.product_id == product)
            valuation_adjustment = 0
            for line in filter_result:
                valuation_adjustment = line.valuation_adjustment
            
            total_balance = 0
            total_input = 0
            total_output = 0
            total_price_in = 0
            total_price_out = 0
            for line in product_lines:
                balance += (line.product_in if line.is_landed_cost == False else 0) - line.product_out
                total_input += (line.product_in if line.is_landed_cost == False else 0)
                total_output += line.product_out
                valuation_initial += line.price_unit
                total_price_in += line.price_unit if line.location_id.usage not in ('internal', 'transit') and line.location_dest_id.usage in ('internal', 'transit') else 0.0
                total_price_out += abs(line.price_unit) if line.location_id.usage in ('internal', 'transit') and line.location_dest_id.usage not in ('internal', 'transit') else 0.0
                row_pos = self._write_line(
                    ws,
                    row_pos,
                    ws_params,
                    col_specs_section="data",
                    render_space={
                        "date": line.date or "",
                        "reference": line.display_name or "",
                        "partner": line.picking_id.partner_id.name or "",
                        "location": line.location_id.name or "",
                        "to": line.location_dest_id.name or "",
                        "input": (line.product_in if line.is_landed_cost == False else 0),
                        "output": line.product_out or 0,
                        "price_unit_in": line.price_unit if line.location_id.usage not in ('internal', 'transit') and line.location_dest_id.usage in ('internal', 'transit') else 0,
                        "price_unit_out": abs(line.price_unit) if line.location_id.usage in ('internal', 'transit') and line.location_dest_id.usage not in ('internal', 'transit') else 0,
                        "price_unit": valuation_initial,
                        "balance": balance,
                    },
                    default_format=FORMATS["format_tcell_amount_right"],
                )
            init = objects._get_initial(
                objects.results.filtered(lambda l: l.product_id == product and l.is_initial)
            )

            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="data",
                col_specs="col_specs_totals",
                wanted_list="wanted_list_totals",

                render_space={
                    "initial": init or 0,
                    "total_input": total_input or 0,
                    "total_output": total_output or 0,
                    "total_price": valuation_initial + valuation_adjustment or 0,
                    "valuation_adjustment": valuation_adjustment or 0,
                    "total_price_in": total_price_in or 0,
                    "total_price_out": total_price_out or 0,
                    "total_balance": balance or 0,
                },
                default_format=FORMATS["format_amount_right_bold"],
            )
        else:

            balance = objects._get_initial(objects.results.filtered(lambda l: l.product_id == product and l.is_initial))
            balance_initil = objects._get_initial(objects.results.filtered(lambda l: l.product_id == product and l.is_initial))

            valuation_initial = sum(objects.results.filtered(lambda l: l.product_id == product and l.is_initial).mapped("price_unit"))

            filter_result = objects.results.filtered(lambda l: l.product_id == product)
            valuation_adjustment = 0
            for line in filter_result:
                valuation_adjustment = line.valuation_adjustment

            product_lines = objects.results.filtered(
                lambda l: l.product_id == product and not l.is_initial
            )

            total_balance = 0
            total_input = 0
            total_output = 0
            total_price = 0
            total_price_in = 0
            total_price_out = 0
            for line in product_lines:
                balance =line.product_in - line.product_out
                total_balance += balance
                total_input += (line.product_in if line.is_landed_cost == False else 0)
                total_output += line.product_out
                total_price += line.price_unit
                total_price_in += line.price_unit if line.location_id.usage not in ('internal', 'transit') and line.location_dest_id.usage in ('internal', 'transit') else 0.0
                total_price_out += abs(line.price_unit) if line.location_id.usage in ('internal', 'transit') and line.location_dest_id.usage not in ('internal', 'transit') else 0.0

            init = objects._get_initial(
                objects.results.filtered(lambda l: l.product_id == product and l.is_initial)
            )

            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="header",
                default_format=FORMATS["format_theader_blue_center"],
                col_specs="col_specs_totals_without_details",
                wanted_list="wanted_list_totals_without_details",
            )

            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="data",
                col_specs="col_specs_totals_without_details",
                wanted_list="wanted_list_totals_without_details",

                render_space={
                    "initial": init or 0,
                    "total_input": total_input or 0,
                    "total_output": total_output or 0,
                    "total_price": total_price + valuation_initial + valuation_adjustment or 0,
                    "total_price_in": total_price_in or 0,
                    "total_price_out": total_price_out or 0,
                    "total_balance": balance_initil + balance or 0,
                    "balance_initial": balance_initil or 0,
                    "valuation_initial": valuation_initial or 0,
                    "valuation_adjustment" : valuation_adjustment or 0
                },
                default_format=FORMATS["format_amount_right_bold"],
            )
