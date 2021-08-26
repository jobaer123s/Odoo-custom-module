from odoo import models
from datetime import date


class statementSMS(models.Model):
    _inherit = 'account.move'

    def send_to_customer_statement_notification(self):

        today = date.today().strftime("%d-%b-%Y")

        inv_obj = self.env['account.move'].sudo()
        search_domain = [('state', '=', 'posted'), ('partner_id', '=', self.partner_id.id)]

        invs = inv_obj.search(search_domain, order='create_date DESC')

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

            for inv in inv_list:

                vals = {
                    'customer_name': self.partner_id.name,
                    'invoice_no': inv.name,
                    'invoice_date': inv.date.strftime('%d-%b-%Y'),
                    'sales_person': inv.invoice_user_id.name,
                    'debit': inv.amount_total if inv.type == 'out_invoice' else 0,
                    'credit': inv.amount_total if inv.type == 'out_refund' else 0,
                    'balance': ''
                }

                customer_invs_list.append(vals)

        msg_text = "Priyo Grahok ({0}),\nNotun Bill: Tk {1} Dr. on {2}, Shorbosesh Bokeya: Tk {3} Dr. Apni Shorbomot Payment Korechen Tk {4}. Jekono Proyojone Call Korun- 01764198266; Office: 02-222299170. Dhonnobad- Cell Electronics Industries Ltd.".format(self.partner_id.name, debit, today, balance, credit)

        sms_obj = self.env['sms.api'].sudo()

        sms_obj.custom_send_sms_api(self.partner_id.mobile, msg_text)

        return True
