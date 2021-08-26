from odoo import  models
from num2words import num2words


class CustomerInvoiceStatement(models.Model):
    _inherit = "account.move"
    _description = "Customer Invoice Statement"

    def custom_invoice_statement(self, partner, current_due):
        print('data is coming......')
        total_balance = 0.00

        inv_obj = self.env['account.move'].sudo()
        search_domain = [('state', '=', 'posted'), ('partner_id', '=', partner)]

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

        previous_balance = total_balance - current_due

        amount_in_words = "".join(num2words(total_balance, lang='en_IN').title().replace("-", " ")).replace(",", "")

        customer_balance = [previous_balance, total_balance, amount_in_words]

        return customer_balance