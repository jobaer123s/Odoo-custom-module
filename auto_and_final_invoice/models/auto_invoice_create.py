from odoo import models


class StockImmediateTransfer(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    def process_auto_invoice(self):
        if str(self.pick_ids.origin).startswith("S0"):
            self.process()
            so = self.env['sale.order'].search([("name", "=", str(self.pick_ids.origin))])
            # so._create_invoices(final=True)
            so._create_invoices()

        return False

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        if res:

            if str(self.pick_ids.origin).startswith("S0"):  # or str(self.pick_ids.origin).startswith("Return of")
                so = self.env['sale.order'].search([("name", "=", str(self.pick_ids.origin))])
                so._create_invoices(final=True)
                return res
        return False


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def create_returns(self):
        # Prevent copy of the carrier and carrier price when generating return picking
        # (we have no integration of returns for now)
        res = super(StockReturnPicking, self).create_returns()

        picking_obj = self.env['stock.picking']
        return_pickings = picking_obj.browse([res['res_id']])

        for picking in return_pickings:
            picking.action_assign()
            picking.action_confirm()
            for mv in picking.move_ids_without_package:
                mv.quantity_done = mv.product_uom_qty
            picking.button_validate()
            # picking.action_done()
            # imediate_rec = imediate_obj.create({'pick_ids': [(4, order.picking_ids.id)]})
            # imediate_rec.process()

        pickings = picking_obj.browse(res['context']['active_ids'])

        for pick in pickings:
            so = self.env['sale.order'].search([("name", "=", str(pick.group_id.name))])
            so._create_invoices(final=True)

        return res


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        self._process()
        for pick in self.pick_ids:
            so = self.env['sale.order'].search([("name", "=", str(pick.group_id.name))])
            so._create_invoices()
