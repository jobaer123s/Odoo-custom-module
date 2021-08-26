from odoo import fields, models


class SaleOrderCustomVat(models.Model):
    _inherit = "sale.order"
    _description = "Sale Order Custom Vat Field"

    sale_order_custom_vat = fields.Monetary(string="Vats")

    def _amount_all(self):
        """ Compute the total amounts of the SO. """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            sale_order_custom_vat = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                sale_order_custom_vat += line.price_vat
            # updating sub total, tax, vat field
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'sale_order_custom_vat': sale_order_custom_vat,
                'amount_total': amount_untaxed + amount_tax + sale_order_custom_vat,
            })
