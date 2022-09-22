from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
