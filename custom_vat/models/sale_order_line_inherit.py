from odoo import fields, models


class SaleOrderLineCustomVat(models.Model):
    _inherit = "sale.order.line"
    _description = "Sale Order Line Custom Vat Field"

    sale_order_line_custom_vat = fields.Many2one(string="Vats", related="product_id.vat_id")

    # added one new field
    price_vat = fields.Float(compute='_compute_amount', string='Total vat', readonly=True, store=True)

    def _compute_amount(self):
        for line in self:

            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            vat = line.sale_order_line_custom_vat.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                              product=line.product_id,
                                                              partner=line.order_id.partner_shipping_id)

            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_vat': sum(t.get('amount', 0.0) for t in vat.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])