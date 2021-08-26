from odoo import fields, models


class CustomVat(models.Model):
    _inherit = 'product.template'
    _description = "Custom vat field"

    vat_id = fields.Many2one('account.tax', string="Customer Vats")
    tax_group_id = fields.Many2one('account.tax.group', string="Tax Group")


