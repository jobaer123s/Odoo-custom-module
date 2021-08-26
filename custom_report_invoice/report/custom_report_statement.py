from odoo import api, fields, models, _, exceptions
from num2words import num2words

class CustomReportStatement(models.Model):
    _inherit = "account.move"
    _description = "Customer Statement"

    def custom_statement_pdf(self):
        total_debit = 0.00
        total_credit = 0.00
        total_balance = 0.00

        inv_obj = self.env['account.move'].sudo()
        search_domain = [('state', '=', 'posted'), ('partner_id', '=', self.partner_id.id), ('journal_id', '=', self.journal_id.id)]

        invs = inv_obj.search(search_domain, order='create_date DESC')

        partner_invs = dict()

        for inv in invs:

            if inv.partner_id.id in partner_invs:
                partner_invs[inv.partner_id.id].append(inv.id)
            else:
                partner_invs[inv.partner_id.id] = [inv.id]

        customer_invs_list = list()
        for partner in partner_invs:
            debit = 0.00
            credit = 0.00

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

            for inv in inv_list:

                vals = {
                    'customer_name': self.partner_id.name,
                    'invoice_no': inv.name,
                    'invoice_date': inv.date.strftime('%d-%b-%Y'),
                    'invoice_type': inv.type,
                    'invoice_ref': inv.ref,
                    'debit': inv.amount_total if inv.type == 'out_invoice' else 0,
                    'credit': inv.amount_total - inv.amount_residual if inv.type == 'out_refund' or inv.type=='out_invoice' else 0,
                    'balance': inv.amount_residual,
                }

                customer_invs_list.append(vals)

        customer_name = self.partner_id.name
        customer_street = self.partner_id.street
        customer_city = self.partner_id.city
        customer_zip = self.partner_id.zip
        customer_mobile = self.partner_id.mobile
        customer_email = self.partner_id.email

        amount_in_words = "".join(num2words(total_balance, lang='en_IN').title().replace("-", " ")).replace(",", "")

        data = {
            'model': 'sale.order',
            'form': self.read()[0],
            'csr': customer_invs_list,
            'customer_name': customer_name,
            'customer_street': customer_street,
            'customer_zip': customer_zip,
            'customer_city': customer_city,
            'customer_mobile': customer_mobile,
            'customer_email': customer_email,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'total_balance': total_balance,
            'amount_in_words': amount_in_words,
        }

        return self.env.ref('custom_report_invoice.custom_report_statement_tmpl').report_action(self, data=data)
