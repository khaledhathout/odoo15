# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', store=True)

    stock_card_valuation_value = fields.Float(string="Valuation Value", compute="_get_stock_valuation_value", store=True)

    @api.depends("stock_valuation_layer_ids")
    def _get_stock_valuation_value(self):
        for rec in self:
            rec.stock_card_valuation_value = sum(
                self.env['stock.valuation.layer'].search([('stock_move_id', '=', rec.id)], limit=1).mapped(
                    "value"))


class StockCardView(models.TransientModel):
    _name = "stock.card.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    is_initial = fields.Boolean()
    is_landed_cost = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    price_unit = fields.Float()
    valuation_adjustment = fields.Float()
    picking_id = fields.Many2one(comodel_name="stock.picking")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference
            if rec.picking_id.origin:
                name = "{} ({})".format(name, rec.picking_id.origin)
            result.append((rec.id, name))
        return result


class StockCardReport(models.TransientModel):
    _name = "report.stock.card.report"
    _description = "Stock Card Report"

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product")
    location_id = fields.Many2many(comodel_name="stock.location")
    category_id = fields.Many2one("product.category", string="Category")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    report_type = fields.Selection([('with_details', 'With Details'), ('without_details', 'Without Details')],
                                   string="Report Type", default="with_details")
    with_details = fields.Boolean()

    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name="stock.card.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        self.date_to = self.date_to or fields.Date.context_today(self)
        locations = self.env["stock.location"].search(
            [("id", "child_of", self.location_id.ids)]
        )

        if self.category_id:
            print("product_ids: ", self.product_ids.ids)
            self._cr.execute(
                """
                SELECT move.date, move.product_id, move.product_qty,
                    move.product_uom_qty, move.product_uom, move.reference,
                    move.location_id, move.location_dest_id, move.stock_card_valuation_value as price_unit,
                    case when move.location_dest_id in %s
                        then move.product_qty end as product_in,
                    case when move.location_id in %s
                        then move.product_qty end as product_out,
                    case when move.date < %s then True else False end as is_initial,
                    move.picking_id
                FROM stock_move move
                INNER JOIN product_product product on product.id = move.product_id
                INNER JOIN product_template template on template.id = product.product_tmpl_id
                WHERE (move.location_id in %s or move.location_dest_id in %s)
                    and move.state = 'done' 
                    and move.product_id in %s
                    and template.categ_id in %s
                    and CAST(move.date AS date) <= %s
                ORDER BY move.date, move.reference
            """,
                (
                    tuple(locations.ids),
                    tuple(locations.ids),
                    date_from,
                    tuple(locations.ids),
                    tuple(locations.ids),
                    tuple(self.product_ids.ids),
                    tuple(self.category_id.ids),
                    self.date_to,
                ),
            )
        else:
            self._cr.execute(
                """
                SELECT  T.date,
                        T.product_id, 
                        T.product_qty,
                        T.product_uom_qty, 
                        T.product_uom, 
                        T.reference,
                        T.location_id, 
                        T.location_dest_id, 
                        T.price_unit as price_unit,
                        T.product_in as product_in,
                        T.product_out as product_out,
                        T.is_initial as is_initial,
                        T.is_landed_cost as is_landed_cost,
                        T.picking_id,
                        (select sum (value) from stock_valuation_layer s where s.company_id = T.company_id 
                                and s.product_id = T.product_id and CAST(s.create_date AS DATE) <= %s and s.stock_move_id IS NULL ) as valuation_adjustment
                    FROM (
                        SELECT  move.date AS date, 
                                move.product_id AS product_id, 
                                move.product_qty AS product_qty,
                                move.product_uom_qty AS product_uom_qty, 
                                move.product_uom AS product_uom, 
                                move.reference AS reference,
                                move.location_id AS location_id, 
                                move.location_dest_id AS location_dest_id, 
                                case when layer.stock_landed_cost_id IS NULL then
                                    move.stock_card_valuation_value else layer.value end as price_unit,
                                case when move.location_dest_id in %s
                                    then move.product_qty end as product_in,
                                case when move.location_id in %s
                                    then move.product_qty end as product_out,
                                case when move.date < %s then True else False end as is_initial,
                                case when layer.stock_landed_cost_id IS NULL then False else True end as is_landed_cost,
                                move.picking_id AS picking_id,
                                move.company_id AS company_id
                        FROM stock_move move
                        Inner Join stock_valuation_layer layer on layer.stock_move_id = move.id
                        WHERE (move.location_id in %s or move.location_dest_id in %s)
                            and move.state = 'done' 
                            and CAST(move.date AS date) <= %s
                        ) T
                ORDER BY T.date, T.reference
                """
                ,
                (
                    self.date_to,
                    tuple(locations.ids),
                    tuple(locations.ids),
                    date_from,
                    tuple(locations.ids),
                    tuple(locations.ids),
                    # tuple(self.warehouse_id.ids),
                    self.date_to,
                ),
            )
        stock_card_results = self._cr.dictfetchall()
        ReportLine = self.env["stock.card.view"]
        self.results = [ReportLine.new(line).id for line in stock_card_results]

    def _get_initial(self, product_line):
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    # def _get_initial_balance(self, product_line):
    #     price_unit = sum(product_line.mapped("product_in"))
    #     product_output_qty = sum(product_line.mapped("product_out"))
    #     return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        if self.report_type == "with_details":
            action = (
                report_type == "xlsx"
                and self.env.ref("stock_card_report.action_stock_card_report_xlsx")
                or self.env.ref("stock_card_report.action_stock_card_report_pdf")
            )
            return action.report_action(self, config=False)
        else:
            action = (
                    report_type == "xlsx"
                    and self.env.ref("stock_card_report.action_stock_card_report_xlsx")
                    or self.env.ref("stock_card_report.action_stock_card_report_pdf_without_details")
            )
            return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report.report_type == "with_details":
            if report:
                rcontext["o"] = report
                result["html"] = self.env.ref(
                    "stock_card_report.report_stock_card_report_html"
                )._render(rcontext)
            return result
        else:
            if report:
                rcontext["o"] = report
                result["html"] = self.env.ref(
                    "stock_card_report.report_stock_card_report_html_without_details"
                )._render(rcontext)
            return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
