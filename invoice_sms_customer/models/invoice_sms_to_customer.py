from odoo import models


class invoiceSMS(models.Model):
    _inherit = 'account.move'

    def send_to_customer_invoice_notification(self):
        invoice_date = self.invoice_date.strftime("%d-%b-%Y") if self.invoice_date else None

        msg_text = "Priyo Grahok ({0}),\nNotun Bill: Tk {1} Dr. on {2}, Apni Pay Korechen Tk {3}, Apnar Bokeya: Tk {4}. Jekono Proyojone Call Korun- 01764198266; Office: 02-222299170. Dhonnobad- Cell Electronics Industries Ltd.".format(self.partner_id.name, self.amount_total_signed, invoice_date, self.amount_total_signed-self.amount_residual_signed, self.amount_residual_signed)

        sms_obj = self.env['sms.api'].sudo()

        sms_obj.custom_send_sms_api(self.partner_id.mobile, msg_text)

        return True
