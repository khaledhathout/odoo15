# Copyright 2021 WeDo Technology
# Website: http://wedotech-s.com
# Email: apps@wedotech-s.com
# Phone:00249900034328 - 00249122005009

from odoo import api, models

class AccountStatementReport(models.AbstractModel):
    _name = 'report.wedo_account_statement_report.account_statement_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        dat = data['form']
        docs = []
        #General Domain
        partner_domain = dat['partner_id'] and [('partner_id', '=', dat['partner_id'])] or []
        state_domain = dat['posted_moves'] and [('move_id.state','=', 'posted')] or [('move_id.state','in',['draft', 'posted'])]
        account_domain = dat['partner_report'] and [('account_id.internal_type','in',['receivable','payable'])] or [('account_id','=',dat['account_id'])]
        company_domain = dat['company_id'] and [('company_id', '=', dat['company_id'])] or []

        currency_domain = []
        if dat['currency_id'] != dat['company_currency_id']:
            currency_domain = [('currency_id', '=', dat['currency_id'])]

        #Initial Balance Domain
        initial_domain = [('date', '<', dat['from_date'])]
        initial_domain += account_domain + partner_domain + state_domain + currency_domain + company_domain

        #General Transaction Domain
        domain=[('date','>=', dat['from_date']),('date','<=',dat['to_date'])]
        domain+= account_domain + partner_domain + state_domain + currency_domain + company_domain

        initial_lines = self.env['account.move.line'].search(initial_domain)
        lines=self.env['account.move.line'].search(domain, order='date, id')

        result = []
        initial_balance = total_debit = total_credit = balance = 0

        #In Case of Currency is Company default currency, get data from debit & Credit Field
        if dat['currency_id'] == dat['company_currency_id']:
            initial_balance = sum([line.debit - line.credit for line in initial_lines])
            balance = initial_balance
            seq = 0
            for line in lines:
                seq += 1
                balance += (line.debit - line.credit)
                name=line.name

                if dat['payment_detail'] and  line.payment_id and line.payment_id.ref:
                    name = line.payment_id.ref+' - '+ line.name

                payment=self.env['account.payment'].search([('name','=',line.name)],limit=1)

                if dat['payment_detail'] and  line.name and payment:
                    name= payment.ref

                res ={
                    'seq': seq,
                    'mno': line.move_id.name,
                    'date': line.date,
                    'name': name,
                    'debit': line.debit,
                    'credit':line.credit,
                    'balance': balance
                }
                result.append(res)

            total_debit = sum(lines.mapped('debit'))
            total_credit = sum(lines.mapped('credit'))

        #Second Case if Currency different from Company default currency, get data from Amount Currency Field
        else:
            initial_balance = sum([line.amount_currency for line in initial_lines])
            balance = initial_balance
            seq = 0
            for line in lines:
                seq += 1
                balance += (line.amount_currency)
                if  dat['payment_detail'] and  line.payment_id and line.payment_id.ref:
                    name = line.payment_id.ref +' - '+ line.name
                else:
                    name = line.name

                res = {
                    'seq': seq,
                    'mno': line.move_id.name,
                    'date': line.date,
                    'name': name,
                    'debit': line.amount_currency > 0 and line.amount_currency or 0,
                    'credit': line.amount_currency < 0 and line.amount_currency or 0,
                    'balance': balance
                }
                result.append(res)

            total_debit = sum([line.amount_currency for line in lines if line.amount_currency > 0])
            total_credit = sum([line.amount_currency for line in lines if line.amount_currency < 0 ])

        docs.append({'data': result})

        return {
            'doc_ids': self.ids,
            'doc_model': 'account.statement.report',
            'docs': result,
            'initial_balance': initial_balance,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'end_balance': balance,
            'data': data['form'],
        }
