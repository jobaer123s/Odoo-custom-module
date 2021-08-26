from odoo import fields, models
import datetime


class ProductLedger(models.Model):
    _name = "product.ledger"
    _description = "Product Wise Customer Ledger Record"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    customer = fields.Many2one("res.partner", string='Customer',
                               domain="[('type', '=', 'contact'), ('active', '=', True)]")

    def product_ledger_pdf(self):
        from_date = self._context.get("from_date", None)
        to_date = self._context.get("to_date", None)
        customer = self._context.get("customer", None)

        invoice_obj = self.env['account.move'].sudo()
        partner_obj = self.env['res.partner'].sudo()

        # new addition
        payment_obj = self.env['account.payment'].sudo()

        search_domain = [('state', '=', 'posted')]
        custom_search_domain = [('state', '=', 'posted')]

        if from_date:
            search_domain.append(('invoice_date', ">=", from_date))
        if to_date:
            search_domain.append(('invoice_date', "<=", to_date))
        if customer:
            search_domain.append(('partner_id', '=', customer))
            custom_search_domain.append(('partner_id', '=', customer))

        invoices = invoice_obj.search(search_domain, order='create_date DESC')
        all_invoices = invoice_obj.search(custom_search_domain, order='create_date DESC')

        partner_invoice = dict()
        customer_invoice = dict()

        print('invoices', len(invoices))
        print('all_invoices', len(all_invoices))

        # date range
        from_to_date_list = []

        def date_range(first_date, last_date, date_list):
            step = datetime.timedelta(days=1)
            start_date = datetime.datetime.strptime(first_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
            while start_date <= end_date:
                date_list.append(start_date)
                start_date += step

        date_range(from_date, to_date, from_to_date_list)

        customer_inv_total_amount = 0
        customer_inv_total_payment = 0

        if len(invoices) == 0:
            print('if')
            data = {
                'model': "product.ledger",
                'form': self.read()[0],
                'csr': [],
                'products': [],
                'customer': '',
                'total_amount': 0,
                'total_payment': 0,
                'total_due': 0,
                'before_due': 0,
                'total_quantity': [],
                'prod_len': 0,
                'total_quantity_list': [],
                'from_date': datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
                'to_date': datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
            }

            return self.env.ref('custom_product_report_ledger.product_ledger_report_tmpl').with_context(
                landscape=True).report_action(self, data=data)

        else:
            print('else')
            for invoice in invoices:
                # try to refactor it later
                if invoice.partner_id.id in partner_invoice:
                    partner_invoice[invoice.partner_id.id].append(invoice.id)
                else:
                    partner_invoice[invoice.partner_id.id] = [invoice.id]

            # function for finding before due
            for item in all_invoices:
                if item.partner_id.id in customer_invoice:
                    customer_invoice[item.partner_id.id].append(item.id)
                else:
                    customer_invoice[item.partner_id.id] = [item.id]

            for customer in customer_invoice:
                customer_invoice_list = invoice_obj.browse(sorted(customer_invoice[customer]))
                customer_created_date = partner_obj.browse(customer).create_date.date()

                customer_active_date_list = []

                # getting due amount till from date
                date_before_from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date() - datetime.timedelta(1)
                step = datetime.timedelta(days=1)
                while customer_created_date <= date_before_from_date:
                    customer_active_date_list.append(customer_created_date)
                    customer_created_date += step

                for inv in customer_invoice_list:
                    if len(customer_active_date_list) < 1:
                        customer_inv_total_amount = 0
                    else:
                        for date in customer_active_date_list:
                            if date == inv.date:
                                for product in inv.invoice_line_ids:
                                    if product.product_id.name:
                                        customer_inv_total_amount += inv.amount_total
                                        break

                            # this comment is important
                            # for paid in invoice_obj.search([('ref', '=', inv.name)]):
                            #     if date == paid.date:
                            #         customer_inv_total_payment += paid.amount_total

                            # new addition
                            for paid in payment_obj.search([('communication', '=', inv.name)]):
                                if date == paid.payment_date:
                                    customer_inv_total_payment += paid.amount

            before_due = customer_inv_total_amount - customer_inv_total_payment

            customer_invoice_list = list()
            customer_name = ''
            sum_quantity = []
            total_quantity = 0
            due = 0

            for partner in partner_invoice:
                invoice_list = invoice_obj.browse(sorted(customer_invoice[partner]))

                # getting the customer name
                customer_name = partner_obj.browse(partner).name

                inv_amount_date_list = []
                inv_amount_list = []
                inv_payment_list = []
                inv_payment_date_list = []
                inv_date_amount_dict = {}
                inv_date_payment_dict = {}

                inv_product_name_set = set()

                for inv in invoice_list:
                    for product in inv.invoice_line_ids:
                        if product.product_id.name:
                            inv_amount_date_list.append(inv.date)
                            inv_amount_list.append(inv.amount_total)
                            break

                    # this comment is important
                    # for pay in invoice_obj.search([('ref', '=', inv.name)]):
                    #     inv_payment_list.append(pay.amount_total)
                    #     inv_payment_date_list.append(pay.date)

                    # new addition
                    for paid in payment_obj.search([('communication', '=', inv.name)]):
                        inv_payment_list.append(paid.amount)
                        inv_payment_date_list.append(paid.payment_date)

                    for product in inv.invoice_line_ids:
                        if product.product_id.name:
                            inv_product_name_set.add(product.product_id.name)

                products = [name for name in inv_product_name_set]

                products = sorted(products)

                def invoice_date_amount_payment(inv_date_list, inv_date_dict, inv_money_list):
                    for key in range(0, len(inv_date_list)):
                        for value in inv_money_list:
                            if len(inv_date_dict) == 0:
                                inv_date_dict[inv_date_list[key]] = value
                                break
                            else:
                                index = key
                                if inv_date_list[key] in inv_date_dict.keys():
                                    first_value = inv_date_dict.get(inv_date_list[key])
                                    second_value = inv_money_list[index]
                                    total = first_value + second_value
                                    inv_date_dict[inv_date_list[key]] = total
                                else:
                                    inv_date_dict[inv_date_list[key]] = inv_money_list[index]
                                break

                invoice_date_amount_payment(inv_amount_date_list, inv_date_amount_dict, inv_amount_list)
                invoice_date_amount_payment(inv_payment_date_list, inv_date_payment_dict, inv_payment_list)

                # generate cumulative count for products
                inv_product_date_list = []
                inv_product_quantity = []
                inv_product_name = []
                name_date_quan_dict = {}

                for date in from_to_date_list:
                    for inv in invoice_list:
                        if date == inv.date:
                            for product in inv.invoice_line_ids:
                                if product.product_id.name:
                                    inv_product_date_list.append(product.date)
                                    inv_product_quantity.append(product.quantity)
                                    inv_product_name.append(product.product_id.name)

                for date in from_to_date_list:
                    for index in range(len(inv_product_date_list)):
                        if date == inv_product_date_list[index]:
                            if tuple([date, inv_product_name[index]]) in name_date_quan_dict:
                                first_quant = name_date_quan_dict[date, inv_product_name[index]]
                                second_quant = inv_product_quantity[index]
                                total = first_quant + second_quant
                                name_date_quan_dict[date, inv_product_name[index]] = total
                            else:
                                name_date_quan_dict[date, inv_product_name[index]] = inv_product_quantity[index]

                # due, total_amount, total_payment and quantity for invoice
                due = before_due
                total_amount = 0
                total_payment = 0

                for date in from_to_date_list:
                    if date in inv_date_amount_dict:
                        amount = inv_date_amount_dict.get(date)
                    else:
                        amount = 0

                    if date in inv_date_payment_dict:
                        payment = inv_date_payment_dict.get(date)
                    else:
                        payment = 0

                    # for finding cumulative quantity of the products
                    names = []
                    quantity = []
                    for keys in name_date_quan_dict:
                        for name in inv_product_name:
                            if date == keys[0] and name == keys[1]:
                                names.append(name)
                                quantity.append(name_date_quan_dict[keys])
                                break

                    # new _code
                    new_names = []
                    for prod_name in products:
                        if prod_name in names:
                            new_names.append(prod_name)
                        else:
                            new_names.append(0)

                    new_prod_quant = []

                    for new in new_names:
                        if new == 0:
                            new_prod_quant.append(0)
                        else:
                            for idx, val in enumerate(names):
                                if new in val:
                                    new_prod_quant.append(quantity[idx])

                    sum_quantity.append(new_prod_quant)
                    due += amount - payment

                    vals = {
                        'date': date,
                        'amount': amount,
                        'payment': payment,
                        'due': due,
                        'quantity': new_prod_quant
                    }

                    total_amount += amount
                    total_payment += payment
                    customer_invoice_list.append(vals)
                    # total_quantity += sum(new_prod_quant)

            print('sum qty: ', sum_quantity)

            if sum_quantity == []:
                sum_quantity_col = 0
                sum_quantity_row = 0
            else:
                sum_quantity_col = len(sum_quantity)
                sum_quantity_row = len(sum_quantity[0])

            total_quantity_list = []
            add_quantity_col = 0

            for m in range(sum_quantity_row):
                for n in range(sum_quantity_col):
                    add_quantity_col += sum_quantity[n][m]

                total_quantity_list.append(add_quantity_col)
                add_quantity_col = 0

            total_due = due
            customer_name = customer_name
            tq = total_quantity
            prod_len = len(products)

            data = {
                'model': "product.ledger",
                'form': self.read()[0],
                'csr': customer_invoice_list,
                'products': products,
                'customer': customer_name,
                'total_amount': total_amount,
                'total_payment': total_payment,
                'total_due': total_due,
                'before_due': before_due,
                'total_quantity': tq,
                'prod_len': prod_len,
                'total_quantity_list': total_quantity_list,
                'from_date': datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
                'to_date': datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
            }

            return self.env.ref('custom_product_report_ledger.product_ledger_report_tmpl').with_context(
                landscape=True).report_action(self, data=data)

    def product_ledger_excel(self):

        data = {
            'from_date': self._context.get('from_date'),
            'to_date': self._context.get('to_date'),
            'customer': self._context.get("customer"),
        }

        return self.env.ref('custom_product_report_ledger.product_ledger_xlsx_report_tmpl').with_context().report_action(self,
                                                                                                         data=data)


class ProductLedgerReportXlsx(models.AbstractModel):
    _name = 'report.custom_product_report_ledger.product_ledger_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, line):
        format0 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format0.set_align('center')
        format0.set_border()
        format1 = workbook.add_format({'font_size': 10, 'align': 'vcenter',  'bold': True})
        format1.set_align('center')
        format1.set_text_wrap()
        format1.set_border()
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter'})
        format2.set_align('center')
        format2.set_border()
        format3 = workbook.add_format({'font_size': 10, 'align': 'right',  'bold': True})
        format3.set_border()

        sheet = workbook.add_worksheet('Sales')

        from_date = self._context.get("from_date", None)
        to_date = self._context.get("to_date", None)
        customer = self._context.get("customer", None)

        row = 4
        col = 1

        invoice_obj = self.env['account.move'].sudo()
        partner_obj = self.env['res.partner'].sudo()
        # new addition
        payment_obj = self.env['account.payment'].sudo()

        search_domain = [('state', '=', 'posted')]
        custom_search_domain = [('state', '=', 'posted')]

        if from_date:
            search_domain.append(('invoice_date', ">=", from_date))
        if to_date:
            search_domain.append(('invoice_date', "<=", to_date))
        if customer:
            search_domain.append(('partner_id', '=', customer))
            custom_search_domain.append(('partner_id', '=', customer))

        invoices = invoice_obj.search(search_domain, order='create_date DESC')
        all_invoices = invoice_obj.search(custom_search_domain, order='create_date DESC')

        partner_invoice = dict()
        customer_invoice = dict()

        # date range
        from_to_date_list = []

        def date_range(first_date, last_date, date_list):
            step = datetime.timedelta(days=1)
            start_date = datetime.datetime.strptime(first_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
            while start_date <= end_date:
                date_list.append(start_date)
                start_date += step

        date_range(from_date, to_date, from_to_date_list)

        if len(invoices) == 0:
            prod_len = 0
            sheet.merge_range(0, 0, 0, prod_len + 3, 'Cell Electronic Industries Ltd.', format0)
            sheet.merge_range(1, 0, 1, prod_len + 3, 'Customer Name: {0}'.format(''), format1)
            sheet.merge_range(2, 0, 2, prod_len + 3, 'Product Wise Customer Ledger: (From: {0} To: {1})'.format(
                datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
                datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%b-%Y')), format1)
            sheet.merge_range(3, 0, 4, 0, 'Date', format1)
            sheet.merge_range(3, 1, 3, prod_len, 'Product', format1)
            sheet.merge_range(3, prod_len + 1, 4, prod_len + 1, 'Amount', format1)
            sheet.merge_range(3, prod_len + 2, 4, prod_len + 2, 'Payment', format1)
            sheet.merge_range(3, prod_len + 3, 4, prod_len + 3, 'Due', format1)

        else:
            for invoice in invoices:
                # try to refactor it later
                if invoice.partner_id.id in partner_invoice:
                    partner_invoice[invoice.partner_id.id].append(invoice.id)
                else:
                    partner_invoice[invoice.partner_id.id] = [invoice.id]

            # function for finding before due
            for item in all_invoices:
                if item.partner_id.id in customer_invoice:
                    customer_invoice[item.partner_id.id].append(item.id)
                else:
                    customer_invoice[item.partner_id.id] = [item.id]

            customer_inv_total_amount = 0
            customer_inv_total_payment = 0

            for customer in customer_invoice:
                customer_invoice_list = invoice_obj.browse(sorted(customer_invoice[customer]))
                customer_created_date = partner_obj.browse(customer).create_date.date()

                customer_active_date_list = []

                # getting due amount till from date
                date_before_from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date() - datetime.timedelta(1)
                step = datetime.timedelta(days=1)
                while customer_created_date <= date_before_from_date:
                    customer_active_date_list.append(customer_created_date)
                    customer_created_date += step

                for inv in customer_invoice_list:
                    if len(customer_active_date_list) < 1:
                        customer_inv_total_amount = 0
                    else:
                        for date in customer_active_date_list:
                            if date == inv.date:
                                for product in inv.invoice_line_ids:
                                    if product.product_id.name:
                                        customer_inv_total_amount += inv.amount_total
                                        break

                            # this comment is important
                            # for paid in invoice_obj.search([('ref', '=', inv.name)]):
                            #     if date == paid.date:
                            #         customer_inv_total_payment += paid.amount_total

                            # new addition
                            for paid in payment_obj.search([('communication', '=', inv.name)]):
                                if date == paid.payment_date:
                                    customer_inv_total_payment += paid.amount

            before_due = customer_inv_total_amount - customer_inv_total_payment

            customer_invoice_list = list()
            customer_name = ''
            sum_quantity = []
            total_quantity = 0
            #
            for partner in partner_invoice:
                invoice_list = invoice_obj.browse(sorted(customer_invoice[partner]))

                # getting the customer name
                customer_name = partner_obj.browse(partner).name

                inv_amount_date_list = []
                inv_amount_list = []
                inv_payment_list = []
                inv_payment_date_list = []
                inv_date_amount_dict = {}
                inv_date_payment_dict = {}

                inv_product_name_set = set()

                for inv in invoice_list:
                    for product in inv.invoice_line_ids:
                        if product.product_id.name:
                            inv_amount_date_list.append(inv.date)
                            inv_amount_list.append(inv.amount_total)
                            break

                    # this comment is important
                    # for pay in invoice_obj.search([('ref', '=', inv.name)]):
                    #     inv_payment_list.append(pay.amount_total)
                    #     inv_payment_date_list.append(pay.date)

                    # new addition
                    for paid in payment_obj.search([('communication', '=', inv.name)]):
                        inv_payment_list.append(paid.amount)
                        inv_payment_date_list.append(paid.payment_date)

                    for product in inv.invoice_line_ids:
                        if product.product_id.name:
                            inv_product_name_set.add(product.product_id.name)

                products = [name for name in inv_product_name_set]

                products = sorted(products)

                prod_len = len(products)

                def invoice_date_amount_payment(inv_date_list, inv_date_dict, inv_money_list):
                    for key in range(0, len(inv_date_list)):
                        for value in inv_money_list:
                            if len(inv_date_dict) == 0:
                                inv_date_dict[inv_date_list[key]] = value
                                break
                            else:
                                index = key
                                if inv_date_list[key] in inv_date_dict.keys():
                                    first_value = inv_date_dict.get(inv_date_list[key])
                                    second_value = inv_money_list[index]
                                    total = first_value + second_value
                                    inv_date_dict[inv_date_list[key]] = total
                                else:
                                    inv_date_dict[inv_date_list[key]] = inv_money_list[index]
                                break

                invoice_date_amount_payment(inv_amount_date_list, inv_date_amount_dict, inv_amount_list)
                invoice_date_amount_payment(inv_payment_date_list, inv_date_payment_dict, inv_payment_list)

                # generate cumulative count for products
                inv_product_date_list = []
                inv_product_quantity = []
                inv_product_name = []
                name_date_quan_dict = {}

                for date in from_to_date_list:
                    for inv in invoice_list:
                        if date == inv.date:
                            for product in inv.invoice_line_ids:
                                if product.product_id.name:
                                    inv_product_date_list.append(product.date)
                                    inv_product_quantity.append(product.quantity)
                                    inv_product_name.append(product.product_id.name)

                for date in from_to_date_list:
                    for index in range(len(inv_product_date_list)):
                        if date == inv_product_date_list[index]:
                            if tuple([date, inv_product_name[index]]) in name_date_quan_dict:
                                first_quant = name_date_quan_dict[date, inv_product_name[index]]
                                second_quant = inv_product_quantity[index]
                                total = first_quant + second_quant
                                name_date_quan_dict[date, inv_product_name[index]] = total
                            else:
                                name_date_quan_dict[date, inv_product_name[index]] = inv_product_quantity[index]

                # due, total_amount, total_payment and quantity for invoice
                due = before_due
                total_amount = 0
                total_payment = 0

                quantity_row = 6
                quantity_col = 1

                amount_row = 6
                amount_col = prod_len+1

                payment_row = 6
                payment_col = prod_len+2

                due_row = 6
                due_col = prod_len+3

                before_due_row = 5
                before_due_col = prod_len+3

                total_row = 6

                sheet.merge_range(before_due_row, 0, before_due_row, before_due_col, 'Previous Dues: '+str(before_due), format3)

                for date in from_to_date_list:
                    if date in inv_date_amount_dict:
                        amount = inv_date_amount_dict.get(date)
                    else:
                        amount = 0

                    total_row += 1

                    sheet.write(amount_row, amount_col, amount, format2)
                    amount_row += 1

                    if date in inv_date_payment_dict:
                        payment = inv_date_payment_dict.get(date)
                    else:
                        payment = 0

                    sheet.write(payment_row, payment_col, payment, format2)
                    payment_row += 1

                    # for finding cumulative quantity of the products
                    names = []
                    quantity = []

                    for keys in name_date_quan_dict:
                        for name in inv_product_name:
                            if date == keys[0] and name == keys[1]:
                                names.append(name)
                                quantity.append(name_date_quan_dict[keys])
                                break

                    new_names = []
                    for prod_name in products:
                        if prod_name in names:
                            new_names.append(prod_name)
                        else:
                            new_names.append(0)

                    new_prod_quant = []

                    for new in new_names:
                        if new == 0:
                            new_prod_quant.append(0)
                        else:
                            for idx, val in enumerate(names):
                                if new in val:
                                    new_prod_quant.append(quantity[idx])

                    sum_quantity.append(new_prod_quant)

                    for prod_quantity in new_prod_quant:
                        sheet.write(quantity_row, quantity_col, prod_quantity, format2)
                        quantity_col+=1

                    quantity_row+=1
                    quantity_col = 1

                    due += amount - payment

                    sheet.write(due_row, due_col, due, format2)
                    due_row += 1

                    vals = {
                        'date': date,
                        'amount': amount,
                        'payment': payment,
                        'due': due,
                        'quantity': new_prod_quant
                    }

                    total_amount += amount
                    total_payment += payment
                    customer_invoice_list.append(vals)
                    total_quantity += sum(new_prod_quant)

            total_due = due
            customer_name = customer_name
            tq = total_quantity

            # sum of quantities (column wise)
            sum_quantity_col = len(sum_quantity)
            sum_quantity_row = len(sum_quantity[0])
            total_quantity_list = []
            add_quantity_col = 0

            # excel column
            total_quantity_col = 1

            for m in range(sum_quantity_row):
                for n in range(sum_quantity_col):
                    add_quantity_col += sum_quantity[n][m]

                total_quantity_list.append(add_quantity_col)
                add_quantity_col = 0

            sheet.set_column(0, prod_len+3, 12)

            sheet.merge_range(0, 0, 0, prod_len+3, 'Cell Electronic Industries Ltd.', format0)
            sheet.merge_range(1, 0, 1, prod_len+3, 'Customer Name: {0}'.format(customer_name.title()), format1)
            sheet.merge_range(2, 0, 2, prod_len+3, 'Product Wise Customer Ledger: (From: {0} To: {1})'.format(
                datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
                datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%b-%Y')), format1)
            sheet.merge_range(3, 0, 4, 0, 'Date', format1)
            sheet.merge_range(3, 1, 3, prod_len, 'Product', format1)

            for prod_name in products:
                sheet.write(row, col, prod_name.title(), format1)
                col+=1

            sheet.merge_range(3, prod_len + 1, 4, prod_len+1, 'Amount', format1)
            sheet.merge_range(3, prod_len + 2, 4, prod_len + 2, 'Payment', format1)
            sheet.merge_range(3, prod_len + 3, 4, prod_len + 3, 'Due', format1)

            date_row = 6
            date_col = 0
            for prod_date in from_to_date_list:
                sheet.write(date_row, date_col, prod_date.strftime('%d-%b-%Y'), format2)
                date_row+=1

            # Total Values (Footer)
            sheet.write(len(from_to_date_list)+6, 0, 'Total', format1)
            for q in total_quantity_list:
                sheet.write(total_row, total_quantity_col, q, format2)
                total_quantity_col+=1

            sheet.write(total_row, prod_len+1, total_amount, format1)
            sheet.write(total_row, prod_len+2, total_payment, format1)
            sheet.write(total_row, prod_len+3, total_due, format1)
