import datetime

from odoo import fields, models


class CustomerLedger(models.Model):
    _name = "customer.ledger"
    _description = "Customer Ledger"

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    customer = fields.Many2one('res.partner', string='Customer', domain="[('type', '=', 'contact'), ('active', '=', True)]")

    def customer_ledger_pdf(self):

        from_date = self._context.get('from_date', None)
        to_date = self._context.get('to_date', None)
        customer = self._context.get('customer', None)

        total_debit = 0
        total_credit = 0
        total_balance = 0

        inv_obj = self.env['account.move'].sudo()
        partner_obj = self.env['res.partner'].sudo()
        search_domain = [('state', '=', 'posted')]

        if from_date:
            search_domain.append(('invoice_date', ">=", from_date))
        if to_date:
            search_domain.append(('invoice_date', "<=", to_date))
        if customer:
            search_domain.append(('partner_id', '=', customer))

        invs = inv_obj.search(search_domain, order='create_date DESC')

        """
        partner_orders = {4736: [2440], 4734: [2407]}
        """
        partner_invs = dict()

        for inv in invs:

            if inv.partner_id.id in partner_invs:
                partner_invs[inv.partner_id.id].append(inv.id)
            else:
                partner_invs[inv.partner_id.id] = [inv.id]

        customer_invs_list = list()
        for partner in partner_invs:
            debit = 0
            credit = 0

            inv_list = inv_obj.browse(sorted(partner_invs[partner]))

            for inv in inv_list:
                if inv.type == 'out_invoice':
                    debit += inv.amount_total
                elif inv.type == 'out_refund':
                    credit += inv.amount_total

                for payment in inv_obj.search([('ref', '=', inv.name)]):
                    credit += payment.amount_total

            balance = debit - credit

            total_debit += debit
            total_credit += credit
            total_balance += balance

            # so_list.reverse()
            customer = partner_obj.browse(partner)
            vals = {
                'order_id': '',
                'order_name': '',
                'order_date': '',
                'customer_name': customer.name,
                'invoice_no': '',
                'invoice_date': '',
                'sales_person': '',
                'product_name': '',
                'quantity': '',
                'unit_price': '',
                'total_price': '',
                'debit': debit,
                'credit': credit,
                'balance': balance
            }
            customer_invs_list.append(vals)

        data = {
            'model': 'sale.order',
            'form': self.read()[0],
            'csr': customer_invs_list,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'total_balance': total_balance,
            'from_date': datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
            'to_date': datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
        }

        return self.env.ref('custom_report_ledger.customer_ledger_report_tmpl').with_context(landscape=False).report_action(self, data=data)