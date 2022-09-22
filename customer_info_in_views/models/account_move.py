from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
