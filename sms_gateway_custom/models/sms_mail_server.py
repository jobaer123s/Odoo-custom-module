from odoo import api, fields, models, _

import requests


class SMSMailServer(models.Model):
    _name = "sms.mail.server"
    _description = "SMS Mail Server"

    @api.model
    def get_reference_type(self):
        return ['SSL Wireless', 'Route Mobile']

    @api.model
    def _get_mob_no(self):
        user_obj = self.env['res.users'].browse([self._uid])
        return user_obj.mob_number

    @api.model
    def _set_mob_no(self):
        user_obj = self.env['res.users'].browse([self._uid])
        user_obj.write({'mob_number': self.user_mobile_no})

    description = fields.Char(string="Description", required=True)

    sequence = fields.Integer(string='Priority', help="Default Priority will be 0.")
    sms_debug = fields.Boolean(string="Debugging",
                               help="If enabled, the error message of sms gateway will be written to the log file")
    user_mobile_no = fields.Char(string="Mobile No.", help="Eleven digit mobile number with country code(e.g +88)")
    # gateway = fields.Selection('get_reference_type')
    gateway = fields.Char(string="Gateway", required=True)

    ssl_url = fields.Char(string="URL", widget="url", required=True)
    ssl_user_name = fields.Char(string="User Name", required=True)
    ssl_password = fields.Char(string="Password", required=True)
    ssl_sid = fields.Selection([("green_dot", "Green Dot"), ("ogroni", "Ogroni")],
                               string="Sender Id", required=True)

    def test_conn_ssl(self):
        self.ensure_one()
        user_obj = self.env['res.users'].browse(self._uid)
        mobile_number = self.user_mobile_no

        mob_numbers_list = mobile_number.split(",")
        sms_text = "This is e test SMS, sent from ERP. Test by Ogroni Informatix Limited"
        data = {
            "user": self.ssl_user_name,
            "pass": self.ssl_password,
            "sid": self.ssl_sid,
        }

        try:

            send_urls = self.ssl_url
            dlr = 1
            smstype = 'TEXT'
            mob_no = ''
            source = 'Ogroni'
            user_name = self.ssl_user_name
            password = self.ssl_password

            for mob_no in mob_numbers_list:

                if len(mob_no) >= 13:
                    mob_no = mob_no
                else:
                    tmp_mob = mob_no[-11:]
                    mob_no = str('+88') + str(tmp_mob)

                request_url = "{0}&userName={1}&password={2}&MsgType={3}&receiver={4}&message={5}".format(send_urls, user_name, password, smstype, mob_no, sms_text)

                resp = requests.post(request_url)
                response_content = resp._content.decode('utf-8')

        except Exception as e:
            print(e)

        return True


class SmsApi(models.AbstractModel):
    _inherit = 'sms.api'

    """
    @api.model
    def _send_sms(self, numbers, message):

        response = self.custom_send_sms_api(numbers, message)
        status = response.status_code

        sms_response = {
                        'res_id': message.get('res_id'),
                        'state': 'success' if status == 200 else 'server_error',
                        'credit': 1
                        }

        return sms_response
    """

    @api.model
    def _send_sms_batch(self, messages):

        response_list = list()

        for message in messages:

            number = str('+88') + str(message.get('number'))[-11:]
            sms_text = message.get('content')

            response = self.custom_send_sms_api(number, sms_text)
            status = response.status_code

            response_list.append({
                'res_id': message.get('res_id'),
                'state': 'success' if status == 200 else 'server_error',
                'credit': 1
            })

        return response_list

    def custom_send_sms_api(self, numbers, message):

        sms_server = self.env['sms.mail.server'].browse(1)

        send_urls = sms_server.ssl_url
        user_name = sms_server.ssl_user_name
        password = sms_server.ssl_password
        dlr = 1
        smstype = 'TEXT'
        source = 'Ogroni'

        request_url = "{0}&userName={1}&password={2}&MsgType={3}&receiver={4}&message={5}".format(send_urls, user_name, password, smstype, numbers, message)

        resp = requests.post(request_url)
        response_content = resp._content.decode('utf-8')

        return resp

    def format_mobile_numbers(self, numbers):

        numbers_str = ''

        for number in numbers:
            numbers_str += str(number)[-11:] + "|"

        if numbers_str.endswith("|"):
            numbers_str = numbers_str[:-1]

        return numbers_str

