from odoo import fields, models


class CustomReference(models.Model):
    _name = "custom.reference"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Custom Customer Reference"

    name = fields.Char(string="Reference Name", required=True)
    remarks = fields.Text(string='Remarks')


class CustomerCustomReferenceField(models.Model):
    _inherit = 'res.partner'
    _description = "Customer Custom Reference Field"

    partner_reference_id = fields.Many2one('custom.reference', string="Reference")


class AddCustomReferenceFieldToSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = "Sale Order Custom Reference Field"

    sale_custom_references = fields.Many2one(string='Reference', related='partner_id.partner_reference_id')


class AddCustomReferenceFieldToAccountMove(models.Model):
    _inherit = 'account.move'
    _description = "Account Move Custom Reference Field"

    account_custom_references = fields.Many2one(string="Reference", related="partner_id.partner_reference_id")
