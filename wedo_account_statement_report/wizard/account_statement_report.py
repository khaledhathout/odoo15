# Copyright 2021 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ReportLine(models.TransientModel):
    _name = "report.line"

    seq = fields.Char(string="Seq")
    mno = fields.Char(string="MNo")
    date = fields.Date("Date",)
    label = fields.Char(string="Label")
    debit = fields.Float(string="Debit")
    credit = fields.Float(string="credit")
    balance = fields.Float(string="Balance")


class AccountStatementReport(models.TransientModel):
    _name = "account.statement.report"
    _description = "Account Statement Report"

    from_date = fields.Date("From Date", default=fields.Date.context_today)
    to_date = fields.Date("To Date", default=fields.Date.context_today)
    account_id = fields.Many2one(
        comodel_name="account.account", string="Account")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    posted_moves = fields.Boolean(string="Posted Moves Only")
    partner_report = fields.Boolean(string="Partner Report")
    payment_detail = fields.Boolean(string="Show Payment Detail", default=True)
    company_id = fields.Many2one(
        comodel_name="res.company", string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency",
                                  default=lambda self: self.env.company.currency_id.id)
    line_id = fields.Many2many('report.line', string="Line")

    # If account has currency read it
    @api.onchange("account_id")
    def _onchange_account_id(self):
        self.currency_id = self.account_id.currency_id and self.account_id.currency_id.id or self.env.company.currency_id.id

    def button_export_xlsx(self):

        # dat = data['form']
        docs = []
        # General Domain
        old_record = self.env['report.line'].search([])
        for line in old_record:
            line.unlink()
        partner_domain = self.partner_id and [
            ('partner_id', '=', self.partner_id.id)] or []
        state_domain = self.posted_moves and [('move_id.state', '=', 'posted')] or [
            ('move_id.state', 'in', ['draft', 'posted'])]
        account_domain = self.partner_report and [('account_id.internal_type', 'in', ['receivable', 'payable'])] or [
            ('account_id', '=', self.account_id.id)]
        company_domain = self.company_id and [
            ('company_id', '=', self.company_id.id)] or []

        currency_domain = []
        if self.currency_id != self.company_id.currency_id:
            currency_domain = [('currency_id', '=', self.currency_id.id)]

        # Initial Balance Domain
        initial_domain = [('date', '<', self.from_date)]
        initial_domain += account_domain + partner_domain + \
            state_domain + currency_domain + company_domain

        # General Transaction Domain
        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]
        domain += account_domain + partner_domain + \
            state_domain + currency_domain + company_domain

        initial_lines = self.env['account.move.line'].search(initial_domain)
        lines = self.env['account.move.line'].search(domain, order='date, id')
        if not lines:
            raise ValidationError(
                'There is no data to print it')
        result = []
        initial_balance = total_debit = total_credit = balance = 0

        # In Case of Currency is Company default currency, get data from debit & Credit Field
        if self.currency_id == self.company_id.currency_id:
            initial_balance = sum(
                [line.debit - line.credit for line in initial_lines])
            balance = initial_balance
            seq = 0
            account_name = ''
            state = ''
            if not self.partner_report:
                account_name = self.account_id.name
            if self.partner_report:
                account_name = self.partner_id.name

            if self.posted_moves:
                state = 'Posted Only'
            if not self.posted_moves:
                state = 'All Moves'

            info = account_name + '-' + self.currency_id.name + '-' + \
                str(self.from_date) + '-'+str(self.to_date) + '-' + state
            firs_line = {
                'label': info,
                'debit': initial_balance > 0 and initial_balance or 0.0,
                'credit':  initial_balance < 0 and initial_balance or 0.0,
                'balance': balance
            }
            self.env['report.line'].create(firs_line)

            for line in lines:
                seq += 1
                balance += (line.debit - line.credit)
                if self.payment_detail and line.payment_id and line.payment_id.ref:
                    name = line.payment_id.ref + ' - ' + line.name
                else:
                    name = line.name
                res = {
                    'seq': seq,
                    'mno': line.move_id.name,
                    'date': line.date,
                    'label': name,
                    'debit': line.debit,
                    'credit': line.credit,
                    'balance': balance
                }
                self.env['report.line'].create(res)
                # result.append(res)

            total_debit = sum(lines.mapped('debit'))
            total_credit = sum(lines.mapped('credit'))

            last_line = {
                'label': 'Total',
                'debit': total_debit,
                'credit': total_credit,
            }

            self.env['report.line'].create(last_line)

        # Second Case if Currency different from Company default currency, get data from Amount Currency Field
        else:
            initial_balance = sum(
                [line.amount_currency for line in initial_lines])
            balance = initial_balance
            seq = 0
            account_name = ''
            state = ''
            if not self.partner_report:
                account_name = self.account_id.name
            if self.partner_report:
                account_name = self.partner_id.name

            if self.posted_moves:
                state = 'Posted Only'
            if not self.posted_moves:
                state = 'All Moves'

            info = account_name + '-' + self.currency_id.name + '-' + str(self.from_date) + '-' + str(
                self.to_date) + '-' + state
            firs_line = {
                'label': info,
                'debit': initial_balance > 0 and initial_balance or 0.0,
                'credit': initial_balance < 0 and initial_balance or 0.0,
                'balance': balance
            }
            self.env['report.line'].create(firs_line)

            for line in lines:
                seq += 1
                balance += (line.amount_currency)
                if self.payment_detail and line.payment_id and line.payment_id.ref:
                    name = line.payment_id.ref + ' - ' + line.name
                else:
                    name = line.name
                res = {
                    'seq': seq,
                    'mno': line.move_id.name,
                    'date': line.date,
                    'label': name,
                    'debit': line.amount_currency > 0 and line.amount_currency or 0,
                    'credit': line.amount_currency < 0 and line.amount_currency or 0,
                    'balance': balance
                }
                self.env['report.line'].create(res)

            total_debit = sum(
                [line.amount_currency for line in lines if line.amount_currency > 0])
            total_credit = sum(
                [line.amount_currency for line in lines if line.amount_currency < 0])
            last_line = {
                'label': 'Total',
                'debit': total_debit,
                'credit': total_credit,
            }

            self.env['report.line'].create(last_line)

        # docs.append({'data': result})

        return {'type': 'ir.actions.act_window',
                'name': 'Export XLSX',
                'res_model': 'report.line',
                'view_mode': 'tree',
                'target': 'current'}

    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': self.from_date,
                'to_date': self.to_date,
                'payment_detail': self.payment_detail,
                'account_id': self.account_id.id,
                'account_name': self.account_id.name,
                'partner_id': self.partner_id.id,
                'partner_name': self.partner_id.name,
                'currency_id': self.currency_id.id,
                'currency_name': self.currency_id.name or '-',
                'posted_moves': self.posted_moves,
                'partner_report': self.partner_report,
                'company_id': self.company_id.id,
                'company_currency_id': self.company_id.currency_id.id,
            },
        }
        return {'type': 'ir.actions.report',
                'report_name': 'wedo_account_statement_report.account_statement_report',
                'report_type': 'qweb-pdf',
                'data': data}

    def export_html(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': self.from_date,
                'to_date': self.to_date,
                'payment_detail': self.payment_detail,
                'account_id': self.account_id.id,
                'account_name': self.account_id.name,
                'partner_id': self.partner_id.id,
                'partner_name': self.partner_id.name,
                'currency_id': self.currency_id.id,
                'currency_name': self.currency_id.name or '-',
                'posted_moves': self.posted_moves,
                'partner_report': self.partner_report,
                'company_id': self.company_id.id,
                'company_currency_id': self.company_id.currency_id.id,
            },
        }
        return {'type': 'ir.actions.report',
                'report_name': 'wedo_account_statement_report.account_statement_report',
                'report_type': 'qweb-html',
                'data': data}

