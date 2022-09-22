from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
