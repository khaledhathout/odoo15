from odoo import models, api, fields,_


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Sale Order Line',copy=False)

    def get_sale_line_id(self):
        self.sale_order_line_id.invoice_lines += self


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    account_move_ids = fields.Many2many('account.move', string='account_move')
    account_move_ids_count = fields.Integer(compute="get_account_move_ids_count")

    @api.depends('account_move_ids')
    def get_account_move_ids_count(self):
        for rec in self :
            rec.account_move_ids_count = len(rec.account_move_ids)

    def action_open_move(self):
        action = {
            'name': _('Refund'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'views': [[False, 'tree'], [False, 'form'], [False, 'kanban']],
            'domain': [('id', 'in', self.account_move_ids.ids)],
            'context': {
                'create': False,
            }
        }
        return action


    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if res == True :
            if (self.picking_type_id.code == 'outgoing' and self.location_dest_id.usage == 'supplier') :
                self.action_create_move('in_refund')
            elif (self.picking_type_id.code == 'incoming' and self.location_id.usage == 'customer'):
                self.action_create_move('out_refund')
        return res

    def action_create_move(self, move_type):
            move_obj = self.env['account.move']
            vals=[]
            for move in self.move_ids_without_package:
                if move_type == 'in_refund' :
                    vals.append((0,0,{
                        'product_id': move.purchase_line_id.product_id.id,
                        'purchase_line_id': move.purchase_line_id.id,
                        'name':  move.purchase_line_id.name,
                        'quantity': move.quantity_done,
                        'price_unit': move.purchase_line_id.price_unit,
                        'tax_ids': [(6, 0, move.purchase_line_id.taxes_id.ids)],
                    }))
                elif move_type == 'out_refund':
                    vals.append((0,0,{
                        'product_id': move.sale_line_id.product_id.id,
                        'sale_order_line_id': move.sale_line_id.id,
                        'name':  move.sale_line_id.name,
                        'quantity': move.quantity_done,
                        'price_unit': move.sale_line_id.price_unit,
                        'tax_ids': [(6, 0, move.sale_line_id.tax_id.ids)],
                    }))
            if move_type == 'in_refund' :
                journal_id = self.env['account.journal'].sudo().search([('company_id','=',self.company_id.id),('type','=','purchase')],limit=1)
            elif move_type == 'out_refund':
                journal_id = self.env['account.journal'].sudo().search([('company_id','=',self.company_id.id),('type','=','sale')],limit=1)
            
            move_id = move_obj.sudo().create({
                'move_type': move_type,
                'journal_id': journal_id.id,
                'partner_id': self.partner_id.id,
                'date': fields.Date.today(),
                # 'ref': self.name,
                'notice':  self.origin,
                'invoice_line_ids': vals
            })
            self.account_move_ids += move_id

            if move_type == 'out_refund':
                for l in move_id.invoice_line_ids:
                    l.get_sale_line_id()
