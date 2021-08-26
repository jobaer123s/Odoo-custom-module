from odoo import fields, models


class InvoiceLineTotal(models.Model):
    _inherit = "account.move"

    invoice_custom_vat = fields.Monetary(string="Vats")

    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])

        totalPayment = 0

        if invoice_ids:
            invoiceId = invoice_ids[0]
            # print('invoiceId', invoiceId)
            self.env.cr.execute(""" select name from account_move  where id = %s """, [invoiceId])
            res = self.env.cr.fetchone()
            invName = res[0]

            self.env.cr.execute(""" select * from account_payment  where communication = %s """, [invName])
            totalPayment1 = self.env.cr.fetchall()
            totalPayment = len(totalPayment1)

        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                UNION
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids), tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
            # print('in_payment_set', in_payment_set)

        else:
            # print('else')
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_vat = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            # print('move.line_ids', move.line_ids)

            for line in move.line_ids:
                if line.product_id.id != False:

                    self.env.cr.execute(""" SELECT tax.amount FROM product_template pr
                               left join account_tax tax ON pr.vat_id = tax.id where pr.id = %s
                               """, [line.product_id.id])
                    res = self.env.cr.fetchone()
                    # print('res', res[0])
                    # print('vatLine', res[0])

                    if res[0] == None:
                        vatLine = 0
                    else:
                        vatLine = res[0]

                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):

                    if line.product_id.id != False:
                        vatPercantage = (line.balance * vatLine) / 100
                        vatAmount1 = vatPercantage
                        total_vat += vatAmount1
                        total += vatAmount1

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency

                        if move.type == 'out_invoice' and total_tax == 0.0:
                            data2 = total_residual * -1
                            data1 = data2 + total_vat
                            if total == data1:
                                totalData = total * -1
                                line.amount_residual = totalData
                                total_residual = totalData

                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency

                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual

                        total_residual -= total_vat
                        totalData = total * -1
                        if total_residual > totalData:
                            if total != 0.0:
                                total_residual = totalData

                        total_residual_currency += line.amount_residual_currency
                        line.amount_residual = total_residual

                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if totalPayment < 1:
                totalData = total * -1
                total_residual = totalData
                if invoice_ids:
                    query = """ UPDATE account_move_line SET amount_residual = %s WHERE move_id = %s """
                    self.env.cr.execute(query, [totalData, invoice_ids[0]])
            else:
                self.env.cr.execute(""" select name, amount_total from account_move  where id = %s """,
                                    [invoice_ids[0]])
                res = self.env.cr.fetchone()
                invName = res[0]
                amount_total = res[1]

                self.env.cr.execute(""" select sum(amount)  from account_payment  where communication = %s """,
                                    [invName])
                sumData = self.env.cr.fetchone()
                totalPaymentAmouunt = sumData[0]

                presentAmount = amount_total - totalPaymentAmouunt
                total_residual = presentAmount
                lineId = move.line_ids[0].id
                query = """ UPDATE account_move_line SET amount_residual = %s WHERE id = %s """
                self.env.cr.execute(query, [total_residual, lineId])

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1

            total_vat1 = total_vat * -1

            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.invoice_custom_vat = total_vat1
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                # print('entry...')
                move.invoice_payment_state = False
                # move.amount_residual = totalValueWithVat
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
                    # print('paid')

            else:
                move.invoice_payment_state = 'not_paid'

