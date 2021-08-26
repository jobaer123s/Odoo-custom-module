import datetime

from odoo import fields, models


class SummarizedCustomerLedger(models.Model):
    _name = "summarized.customer.ledger"
    _description = "Summarized Customer Ledger"

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    customer = fields.Many2one('res.partner', string='Customer', domain="[('type', '=', 'contact'), ('active', '=', True)]")
    sales_person = fields.Many2one('res.users', string='Sales Person', readonly=False)

    def summarized_customer_ledger_pdf(self):

        from_date = self._context.get('from_date', None)
        to_date = self._context.get('to_date', None)
        customer = self._context.get('customer', None)
        sales_person = self._context.get('sales_person', None)

        sales_person_ranking_dict = dict()
        sales_person_ranking_list = list()

        total_debit = 0
        total_credit = 0
        total_balance = 0
        grand_total_sale = 0

        inv_obj = self.env['account.move'].sudo()
        # so_obj = self.env['sale.order'].sudo()
        partner_obj = self.env['res.partner'].sudo()
        search_domain = [('state', '=', 'posted')]

        if from_date:
            search_domain.append(('invoice_date', ">=", from_date))
        if to_date:
            search_domain.append(('invoice_date', "<=", to_date))
        if customer:
            search_domain.append(('partner_id', '=', customer))
        if sales_person:
            search_domain.append(('invoice_user_id', '=', sales_person))

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

            for inv in inv_list:

                vals = {
                    'order_id': '',
                    'order_name': inv.name,
                    'order_date': '',
                    'customer_name': '',
                    'invoice_no': inv.name,
                    'invoice_date': inv.date.strftime('%d-%b-%Y'),
                    'sales_person': inv.invoice_user_id.name,
                    'product_name': '',
                    'quantity': '',
                    'unit_price': '',
                    'total_price': '',
                    'debit': inv.amount_total if inv.type == 'out_invoice' else 0,
                    'credit': inv.amount_total if inv.type == 'out_refund' else 0,
                    'balance': ''
                }

                customer_invs_list.append(vals)

                # sales_person_ranking_dict
                if inv.invoice_user_id.id in sales_person_ranking_dict:
                    debit = inv.amount_total if inv.type == 'out_invoice' else 0
                    credit = inv.amount_total if inv.type == 'out_refund' else 0
                    total_sale = sales_person_ranking_dict[inv.invoice_user_id.id]['debit'] - sales_person_ranking_dict[inv.invoice_user_id.id]['credit']
                    # grand_total_sale += total_sale

                    sales_person_ranking_dict[inv.invoice_user_id.id]['debit'] += debit
                    sales_person_ranking_dict[inv.invoice_user_id.id]['credit'] += credit
                    sales_person_ranking_dict[inv.invoice_user_id.id]['total_sale'] = total_sale

                else:
                    debit = inv.amount_total if inv.type == 'out_invoice' else 0
                    credit = inv.amount_total if inv.type == 'out_refund' else 0

                    total_sale = debit - credit
                    # grand_total_sale += total_sale

                    sales_person_ranking_dict[inv.invoice_user_id.id] = {
                        'sales_person_id': inv.invoice_user_id.id,
                        'sales_person_name': inv.invoice_user_id.name,
                        'debit': debit,
                        'credit': credit,
                        'total_sale': total_sale,
                        'percentage': 0
                    }

                for payment in inv_obj.search([('ref', '=', inv.name)]):
                    vals = {
                        'order_id': '',
                        'order_name': '',
                        'order_date': '',
                        'customer_name': '',
                        'invoice_no': '',
                        'invoice_date': '',
                        'sales_person': '',
                        'product_name': payment.name,
                        'quantity': '',
                        'unit_price': '',
                        'total_price': '',
                        'debit': '',
                        'credit': payment.amount_total,
                        'balance': ''
                    }

                    customer_invs_list.append(vals)

        # sales_person_ranking_list
        for key in sales_person_ranking_dict:
            grand_total_sale += sales_person_ranking_dict[key]['total_sale']

        for key in sales_person_ranking_dict:
            sale_percent = (sales_person_ranking_dict[key]['total_sale'] / grand_total_sale) * 100
            sales_person_ranking_dict[key]['percentage'] = round(sale_percent, 2)
            sales_person_ranking_list.append(sales_person_ranking_dict[key])

        sales_person_ranking_list_sorted = sorted(sales_person_ranking_list, key=lambda i: i['total_sale'],
                                                  reverse=True)

        data = {
            'model': 'sale.order',
            'form': self.read()[0],
            'csr': customer_invs_list,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'total_balance': total_balance,
            'from_date': datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
            'to_date': datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
            'sp_sale': sales_person_ranking_list_sorted
        }

        return self.env.ref('custom_report_ledger.summarized_customer_ledger_report_tmpl').with_context(landscape=True).report_action(self, data=data)
