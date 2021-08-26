from odoo import api, fields, models, _
from odoo.exceptions import UserError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}


class account_payment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, default_fields):
        rec = super(account_payment, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec

        invoices = self.env['account.move'].browse(active_ids).filtered(
            lambda move: move.is_invoice(include_receipts=True))
        # print('invoices', invoices)

        # Check all invoices are open
        if not invoices or any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        # Check if, in batch payments, there are not negative invoices and positive invoices
        dtype = invoices[0].type
        for inv in invoices[1:]:
            if inv.type != dtype:
                if ((dtype == 'in_refund' and inv.type == 'in_invoice') or
                        (dtype == 'in_invoice' and inv.type == 'in_refund')):
                    raise UserError(
                        _("You cannot register payments for vendor bills and supplier refunds at the same time."))
                if ((dtype == 'out_refund' and inv.type == 'out_invoice') or
                        (dtype == 'out_invoice' and inv.type == 'out_refund')):
                    raise UserError(
                        _("You cannot register payments for customer invoices and credit notes at the same time."))

        amount = self._compute_payment_amount(invoices, invoices[0].currency_id, invoices[0].journal_id,
                                              rec.get('payment_date') or fields.Date.today())


        rec.update({
            'currency_id': invoices[0].currency_id.id,
            'amount': abs(amount),
            'payment_type': 'inbound' if abs(amount) > 0 else 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'communication': invoices[0].invoice_payment_ref or invoices[0].ref or invoices[0].name,
            'invoice_ids': [(6, 0, invoices.ids)],
        })
        return rec

    def _compute_payment_amount(self, invoices, currency, journal, date):

        # custom query

        self.env.cr.execute(
            """ select name, invoice_custom_vat, amount_untaxed, amount_tax, amount_residual from account_move  where id = %s """,
            [invoices.ids[0]])
        res = self.env.cr.fetchone()
        invName = res[0]
        invoice_custom_vat = res[1]
        amount_untaxed = res[2]
        amount_tax = res[3]
        amount_residual1 = res[4]

        self.env.cr.execute(""" select * from account_payment  where communication = %s """, [invName])
        totalPayment1 = self.env.cr.fetchall()
        totalPayment = len(totalPayment1)

        if totalPayment < 1:
            total = amount_untaxed + amount_tax + invoice_custom_vat

        else:
            query = """ UPDATE account_move_line SET amount_residual = %s WHERE move_id = %s """
            self.env.cr.execute(query, [amount_residual1, invoices.ids[0]])
            total = 0.0
        company = journal.company_id
        currency = currency or journal.currency_id or company.currency_id
        date = date or fields.Date.today()

        if not invoices:
            return 0.0

        self.env['account.move'].flush(['type', 'currency_id'])
        self.env['account.move.line'].flush(['amount_residual', 'amount_residual_currency', 'move_id', 'account_id'])
        self.env['account.account'].flush(['user_type_id'])
        self.env['account.account.type'].flush(['type'])
        self._cr.execute('''
            SELECT
                move.type AS type,
                move.currency_id AS currency_id,
                SUM(line.amount_residual) AS amount_residual,
                SUM(line.amount_residual_currency) AS residual_currency
            FROM account_move move
            LEFT JOIN account_move_line line ON line.move_id = move.id
            LEFT JOIN account_account account ON account.id = line.account_id
            LEFT JOIN account_account_type account_type ON account_type.id = account.user_type_id
            WHERE move.id IN %s
            AND account_type.type IN ('receivable', 'payable')
            GROUP BY move.id, move.type
        ''', [tuple(invoices.ids)])
        query_res = self._cr.dictfetchall()

        for res in query_res:
            move_currency = self.env['res.currency'].browse(res['currency_id'])
            if totalPayment < 1:
                total = total
            else:
                if move_currency == currency and move_currency != company.currency_id:
                    total += res['residual_currency']
                else:
                    total += company.currency_id._convert(res['amount_residual'], currency, company, date)
        return total
