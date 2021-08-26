from odoo import fields, models
import datetime


class CustomSalesReport(models.Model):
    _name = "sales.report"
    _description = "Custom Sales Report For All Customers"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def sales_report_pdf(self):
        from_date = self._context.get("from_date", None)
        to_date = self._context.get("to_date", None)

        invoice_obj = self.env['account.move'].sudo()
        partner_obj = self.env['res.partner'].sudo()
        payment_obj = self.env['account.payment'].sudo()

        search_domain = [('state', '=', 'posted')]
        custom_search_domain = [('state', '=', 'posted')]

        # new changes
        search_domain.append(('type', "=", 'out_invoice'))
        custom_search_domain.append(('type', "=", 'out_invoice'))

        if from_date:
            search_domain.append(('invoice_date', ">=", from_date))
        if to_date:
            search_domain.append(('invoice_date', "<=", to_date))

        invoices = invoice_obj.search(search_domain, order='create_date DESC')
        all_invoices = invoice_obj.search(custom_search_domain, order='create_date DESC')

        # date range
        from_to_date_list = []
        products = []

        def date_range(first_date, last_date, date_list):
            step = datetime.timedelta(days=1)
            start_date = datetime.datetime.strptime(first_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
            while start_date <= end_date:
                date_list.append(start_date)
                start_date += step

        date_range(from_date, to_date, from_to_date_list)

        partner_invoice = dict()
        customer_invoice = dict()

        for invoice in invoices:
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

        customer_invoice_list = list()
        customer_names = []
        sum_quantity = []
        total_amount = 0
        total_payment = 0

        total_current_due = 0
        total_previous_due = 0
        total_dues = 0
        # finding previous dues for customers

        for partner in partner_invoice:
            invoice_list = invoice_obj.browse(sorted(partner_invoice[partner]))
            for inv in invoice_list:
                for product in inv.invoice_line_ids:
                    if product.product_id.name:
                        products.append(product.product_id.name)

            total_prods = sorted(list(set(products)))

        for partner in partner_invoice:
            invoice_list = invoice_obj.browse(sorted(partner_invoice[partner]))

            # getting the customer name
            customer_name = partner_obj.browse(partner).name
            print(customer_name)

            # finding amounts and payments for customer
            inv_amount_list = []
            inv_payment_list = []

            # inv_product_name_set = set()

            for inv in invoice_list:
                for product in inv.invoice_line_ids:
                    if product.product_id.name:
                        inv_amount_list.append(inv.amount_total)
                        break

                #this comment is important

                # for pay in invoice_obj.search([('ref', '=', inv.name)]):
                #     inv_payment_list.append(pay.amount_total)

                for pay in payment_obj.search([('communication', '=', inv.name)]):
                    inv_payment_list.append(pay.amount)

            print(inv_payment_list)
            total_inv_current_amount = sum(inv_amount_list)
            total_inv_current_payment = sum(inv_payment_list)

            # finding previous due amount till from date
            all_customer_invoice_list = invoice_obj.browse(sorted(customer_invoice[partner]))
            customer_created_date = partner_obj.browse(partner).create_date.date()

            customer_active_date_list = []

            date_before_from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date() - datetime.timedelta(1)
            step = datetime.timedelta(days=1)
            while customer_created_date <= date_before_from_date:
                customer_active_date_list.append(customer_created_date)
                customer_created_date += step

            customer_inv_total_amount = []
            customer_inv_total_payment = []

            for inv in all_customer_invoice_list:
                for date in customer_active_date_list:
                    if date == inv.date:
                        for product in inv.invoice_line_ids:
                            if product.product_id.name:
                                customer_inv_total_amount.append(inv.amount_total)
                                break
                    # this comment is important
                    # for paid in invoice_obj.search([('ref', '=', inv.name)]):
                    #     if date == paid.date:
                    #         customer_inv_total_payment.append(paid.amount_total)
                    for pay in payment_obj.search([('communication', '=', inv.name)]):
                        if date == pay.payment_date:
                            customer_inv_total_payment.append(pay.amount)
            customer_names.append(customer_name)
            total_prev_inv_amount = sum(customer_inv_total_amount)
            total_prev_inv_payment = sum(customer_inv_total_payment)

            # finding quantities of products
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

            inv_quantity = []
            prod_names = []
            name_quant = {}
            item_quant_list = []

            for val in name_date_quan_dict.values():
                inv_quantity.append(val)

            for key, values in name_date_quan_dict:
                prod_names.append(values)

            for i in range(len(prod_names)):
                if prod_names[i] not in name_quant.keys():
                    name_quant[prod_names[i]] = inv_quantity[i]
                else:
                    name_quant[prod_names[i]] += inv_quantity[i]

            # print(name_quant)

            new_item_name_quant = {}
            for item in total_prods:
                if item in name_quant:
                    new_item_name_quant[item] = name_quant[item]
                else:
                    new_item_name_quant[item] = 0

            # print(new_item_name_quant)

            for prod_qty in new_item_name_quant:
                item_quant_list.append(new_item_name_quant[prod_qty])

            # print(item_quant_list)
            sum_quantity.append(item_quant_list)
            current_due = total_inv_current_amount - total_inv_current_payment
            previous_due = total_prev_inv_amount - total_prev_inv_payment
            total_due = current_due + previous_due

            vals = {
                'name': customer_name,
                'amount': total_inv_current_amount,
                'payment': total_inv_current_payment,
                'current_due': current_due,
                'previous_due': previous_due,
                'total_due': total_due,
                'quantity': item_quant_list
            }
            customer_invoice_list.append(vals)

            total_current_due += current_due
            total_amount += total_inv_current_amount
            total_payment += total_inv_current_payment
            total_previous_due += previous_due
            total_dues += total_due

        # sum of quantities (column wise)
        sum_quantity_col = len(sum_quantity)
        sum_quantity_row = len(sum_quantity[0])
        total_quantity_list = []
        add_quantity_col = 0

        for m in range(sum_quantity_row):
            for n in range(sum_quantity_col):
                add_quantity_col += sum_quantity[n][m]

            # print(total_quantity_list)
            total_quantity_list.append(add_quantity_col)
            add_quantity_col = 0

        # all_customer_names = customer_names
        products = total_prods
        prod_len = len(products)

        data = {
            'model': "sales.report",
            'form': self.read()[0],
            'csr': customer_invoice_list,
            'products': products,
            'total_amount': total_amount,
            'total_payment': total_payment,
            'total_current_due': total_current_due,
            'total_previous_due': total_previous_due,
            'total_dues': total_dues,
            'prod_len': prod_len,
            'total_quantity_list': total_quantity_list,
            'from_date': datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
            'to_date': datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
        }

        return self.env.ref('custom_sales_report.sales_pdf_report_tmpl').with_context(
            landscape=True).report_action(self, data=data)

    def sales_report_excel(self):

        data = {
            'from_date': self._context.get('from_date'),
            'to_date': self._context.get('to_date'),
        }
        return self.env.ref('custom_sales_report.sales_xlsx_report_tmpl').with_context().report_action(self, data=data)


#
class SalesReportXlsx(models.AbstractModel):
    _name = 'report.custom_sales_report.sales_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, line):
        format0 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format0.set_align('center')
        format0.set_border()
        format1 = workbook.add_format({'font_size': 10, 'align': 'vcenter', 'bold': True})
        format1.set_align('center')
        format1.set_text_wrap()
        format1.set_border()
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter'})
        format2.set_align('center')
        format2.set_border()
        format3 = workbook.add_format({'font_size': 10, 'align': 'right', 'bold': True})
        format3.set_border()

        sheet = workbook.add_worksheet('Sales')

        from_date = self._context.get("from_date", None)
        to_date = self._context.get("to_date", None)

        row = 3
        col = 1

        invoice_obj = self.env['account.move'].sudo()
        partner_obj = self.env['res.partner'].sudo()
        payment_obj = self.env['account.payment'].sudo()

        search_domain = [('state', '=', 'posted')]
        custom_search_domain = [('state', '=', 'posted')]

        search_domain.append(('type', "=", 'out_invoice'))
        custom_search_domain.append(('type', "=", 'out_invoice'))

        if from_date:
            search_domain.append(('invoice_date', ">=", from_date))
        if to_date:
            search_domain.append(('invoice_date', "<=", to_date))

        invoices = invoice_obj.search(search_domain, order='create_date DESC')
        all_invoices = invoice_obj.search(custom_search_domain, order='create_date DESC')

        # date range
        from_to_date_list = []
        products = []

        def date_range(first_date, last_date, date_list):
            step = datetime.timedelta(days=1)
            start_date = datetime.datetime.strptime(first_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
            while start_date <= end_date:
                date_list.append(start_date)
                start_date += step

        date_range(from_date, to_date, from_to_date_list)

        partner_invoice = dict()
        customer_invoice = dict()

        for invoice in invoices:
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

        customer_invoice_list = list()

        customer_names = []
        sum_quantity = []
        total_amount = 0
        total_payment = 0

        total_current_due = 0
        total_previous_due = 0
        total_dues = 0

        for partner in partner_invoice:
            invoice_list = invoice_obj.browse(sorted(partner_invoice[partner]))
            for inv in invoice_list:
                for product in inv.invoice_line_ids:
                    if product.product_id.name:
                        products.append(product.product_id.name)

            total_prods = sorted(list(set(products)))

            prod_len = len(total_prods)
            quantity_row = 4
            quantity_col = 1

            amount_row = 4
            amount_col = prod_len + 1

            payment_row = 4
            payment_col = prod_len + 2

            current_due_row = 4
            current_due_col = prod_len + 3

            previous_due_row = 4
            previous_due_col = prod_len + 4

            total_due_row = 4
            total_due_col = prod_len + 5

            total_row = 4

        # finding previous dues for customers
        for partner in partner_invoice:
            invoice_list = invoice_obj.browse(sorted(partner_invoice[partner]))

            # getting the customer name
            customer_name = partner_obj.browse(partner).name
            print(customer_name)

            # finding amounts and payments for customer
            inv_amount_list = []
            inv_payment_list = []

            for inv in invoice_list:
                for product in inv.invoice_line_ids:
                    if product.product_id.name:
                        inv_amount_list.append(inv.amount_total)
                        break

                # this comment is important
                # for pay in invoice_obj.search([('ref', '=', inv.name)]):
                #     inv_payment_list.append(pay.amount_total)

                for pay in payment_obj.search([('communication', '=', inv.name)]):
                    inv_payment_list.append(pay.amount)

            total_inv_current_amount = sum(inv_amount_list)
            total_inv_current_payment = sum(inv_payment_list)

            # finding previous due amount till from date
            all_customer_invoice_list = invoice_obj.browse(sorted(customer_invoice[partner]))
            customer_created_date = partner_obj.browse(partner).create_date.date()

            customer_active_date_list = []

            date_before_from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date() - datetime.timedelta(1)
            step = datetime.timedelta(days=1)
            while customer_created_date <= date_before_from_date:
                customer_active_date_list.append(customer_created_date)
                customer_created_date += step

            customer_inv_total_amount = []
            customer_inv_total_payment = []

            for inv in all_customer_invoice_list:
                for date in customer_active_date_list:
                    if date == inv.date:
                        for product in inv.invoice_line_ids:
                            if product.product_id.name:
                                customer_inv_total_amount.append(inv.amount_total)
                                break
                    # this comment is important
                    # for paid in invoice_obj.search([('ref', '=', inv.name)]):
                    #     if date == paid.date:
                    #         customer_inv_total_payment.append(paid.amount_total)

                    for pay in payment_obj.search([('communication', '=', inv.name)]):
                        if date == pay.payment_date:
                            customer_inv_total_payment.append(pay.amount)

            customer_names.append(customer_name)
            total_prev_inv_amount = sum(customer_inv_total_amount)
            total_prev_inv_payment = sum(customer_inv_total_payment)

            # finding quantities of products
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

            inv_quantity = []
            prod_names = []
            name_quant = {}
            item_quant_list = []

            for val in name_date_quan_dict.values():
                inv_quantity.append(val)

            for key, values in name_date_quan_dict:
                prod_names.append(values)

            for i in range(len(prod_names)):
                if prod_names[i] not in name_quant.keys():
                    name_quant[prod_names[i]] = inv_quantity[i]
                else:
                    name_quant[prod_names[i]] += inv_quantity[i]

            # # print(name_quant)
            # total_prods = sorted(list(set(products)))

            new_item_name_quant = {}
            for item in total_prods:
                if item in name_quant:
                    new_item_name_quant[item] = name_quant[item]
                else:
                    new_item_name_quant[item] = 0

            # print(new_item_name_quant)

            for prod_qty in new_item_name_quant:
                item_quant_list.append(new_item_name_quant[prod_qty])

            # print(item_quant_list)
            sum_quantity.append(item_quant_list)
            current_due = total_inv_current_amount - total_inv_current_payment
            previous_due = total_prev_inv_amount - total_prev_inv_payment
            total_due = current_due + previous_due

            # writing in xl file
            total_row += 1

            sheet.write(amount_row, amount_col, total_inv_current_amount, format2)
            amount_row += 1

            sheet.write(payment_row, payment_col, total_inv_current_payment, format2)
            payment_row += 1

            sheet.write(current_due_row, current_due_col, current_due, format2)
            current_due_row += 1

            sheet.write(previous_due_row, previous_due_col, previous_due, format2)
            previous_due_row += 1

            sheet.write(total_due_row, total_due_col, total_due, format2)
            total_due_row += 1

            for prod_quantity in item_quant_list:
                sheet.write(quantity_row, quantity_col, prod_quantity, format2)
                quantity_col += 1

            quantity_row += 1
            quantity_col = 1

            vals = {
                'name': customer_name,
                'amount': total_inv_current_amount,
                'payment': total_inv_current_payment,
                'current_due': current_due,
                'previous_due': previous_due,
                'total_due': total_due,
                'quantity': item_quant_list
            }

            customer_invoice_list.append(vals)

            total_current_due += current_due
            total_amount += total_inv_current_amount
            total_payment += total_inv_current_payment
            total_previous_due += previous_due
            total_dues += total_due

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

        products = total_prods

        sheet.set_column(0, prod_len + 3, 12)

        sheet.merge_range(0, 0, 0, prod_len + 5, 'Cell Electronic Industries Ltd.', format0)
        sheet.merge_range(1, 0, 1, prod_len + 5, 'Sales Report: (From: {0} To: {1})'.format(
            datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%b-%Y'),
            datetime.datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%b-%Y')), format1)
        sheet.merge_range(2, 0, 3, 0, 'Customer Name', format1)
        sheet.merge_range(2, 1, 2, prod_len, 'Products', format1)

        for prod_name in products:
            sheet.write(row, col, prod_name.title(), format1)
            col += 1

        sheet.merge_range(2, prod_len + 1, 3, prod_len + 1, 'Total Sales', format1)
        sheet.merge_range(2, prod_len + 2, 3, prod_len + 2, 'Total Collections', format1)
        sheet.merge_range(2, prod_len + 3, 3, prod_len + 3, 'Current Dues', format1)
        sheet.merge_range(2, prod_len + 4, 3, prod_len + 4, 'Previous Dues', format1)
        sheet.merge_range(2, prod_len + 5, 3, prod_len + 5, 'Total Dues', format1)

        customer_name_row = 4
        customer_name_col = 0

        for customer_name in customer_names:
            sheet.write(customer_name_row, customer_name_col, customer_name, format2)
            customer_name_row += 1

        # Total Values (Footer)
        sheet.write(len(customer_names) + 4, 0, 'Total', format1)
        for q in total_quantity_list:
            sheet.write(total_row, total_quantity_col, q, format2)
            total_quantity_col += 1

        sheet.write(total_row, prod_len + 1, total_amount, format1)
        sheet.write(total_row, prod_len + 2, total_payment, format1)
        sheet.write(total_row, prod_len + 3, total_current_due, format1)
        sheet.write(total_row, prod_len + 4, total_previous_due, format1)
        sheet.write(total_row, prod_len + 5, total_dues, format1)
