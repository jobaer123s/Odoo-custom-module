from odoo import  fields, models


class InvoiceLine(models.Model):
    _inherit = 'account.move.line'
    vat_ids = fields.Many2one('account.tax', string='Vats', related='product_id.vat_id')