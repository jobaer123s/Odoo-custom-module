from odoo import api, models, _, exceptions


class CustomerLedgerReportPdf(models.Model):
    _name = "report.auto_and_final_invoice.actual_sales_statement_report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        # docids = [70, 69]
        # sales_data = list()

        if len(docids) > 1:
            raise exceptions.ValidationError(_('Multiple Actual Sales Statement can not be print!!!'))
        else:
            sales = self.env['sale.order'].browse(docids)

            for sale in sales:

                actual_sale = dict()
                invoice_products_list = list()
                returned_products_list = list()
                actual_sale_products_list = list()

                # customer address
                customer_address = sale.partner_id.street + ", " if sale.partner_id.street else "" + sale.partner_id.street2 + ", " if sale.partner_id.street2 else "" + sale.partner_id.city + ", " if sale.partner_id.city else ""
                if customer_address.endswith(", "):
                    customer_address = customer_address[:-2]
                if not customer_address:
                    customer_address = ''
                
                # delivery address
                delivery_address = sale.partner_shipping_id.street + ", " if sale.partner_shipping_id.street else "" + sale.partner_shipping_id.street2 + ", " if sale.partner_shipping_id.street2 else "" + sale.partner_shipping_id.city + ", " if sale.partner_shipping_id.city else ""
                if delivery_address.endswith(", "):
                    delivery_address = delivery_address[:-2]
                if not delivery_address:
                    delivery_address = ''

                actual_sale["so"] = str(sale.name)
                actual_sale["so_date"] = str(sale.date_order).split(" ")[0]
                actual_sale["customer"] = sale.partner_id.name
                actual_sale["customer_address"] = customer_address
                actual_sale["delivery_address"] = delivery_address
                actual_sale["customer_mobile"] = sale.partner_id.mobile if sale.partner_id.mobile else ''
                actual_sale["customer_secondary_mobile"] = sale.partner_id.secondary_mobile if sale.partner_id.secondary_mobile else ''
                actual_sale["payment_type"] = sale.payment_type if sale.payment_type else ''

                actual_sale["so_for"] = " ".join(sale.so_for.split("_")).title() if sale.so_for else ''
                actual_sale["technician_name"] = sale.technician_name.name if sale.technician_name else ''
                actual_sale["invoice_names"] = list()
                actual_sale["invoice_dates"] = list()
                actual_sale["ref_invoice_names"] = list()
                actual_sale["ref_invoice_dates"] = list()
                actual_sale["amount_total"] = 0.0

                actual_sale["main_products"] = list()
                actual_sale["invoice_products"] = dict()
                actual_sale["returned_products"] = dict()
                actual_sale["actual_sale_products"] = dict()

                # prepare the invoice and return products
                for invoice in sale.invoice_ids:
                    
                    if invoice.type == "out_invoice":
                        actual_sale["invoice_names"].append(str(invoice.name))
                        actual_sale["invoice_dates"].append(str(invoice.date))
                        actual_sale["amount_total"] = actual_sale["amount_total"] + invoice.amount_total
                    elif invoice.type == "out_refund":
                        actual_sale["ref_invoice_names"].append(str(invoice.name))
                        actual_sale["ref_invoice_dates"].append(str(invoice.date))
                        actual_sale["amount_total"] = actual_sale["amount_total"] - invoice.amount_total

                    for inv_line in invoice.invoice_line_ids:
                        # move_id
                        if invoice.type == "out_invoice":

                            if inv_line.quantity < 0:
                                actual_sale["returned_products"][str(inv_line.product_id.id)] = {
                                    "name": str(inv_line.product_id.name),
                                    "quantity": -1 * inv_line.quantity,
                                    "price_unit": inv_line.price_unit,
                                    "price_subtotal": inv_line.price_subtotal,
                                    "discount": 0,
                                    "tax": 0,
                                    "price_total": inv_line.price_total
                                }
                            else:

                                if str(inv_line.product_id.id) in actual_sale["invoice_products"]:

                                    # actual_sale["invoice_products"][str(inv_line.product_id.id)] = {
                                    actual_sale["invoice_products"][str(inv_line.product_id.id)]["quantity"] = actual_sale["invoice_products"][str(inv_line.product_id.id)]["quantity"] + inv_line.quantity

                                    actual_sale["invoice_products"][str(inv_line.product_id.id)]["price_unit"] = inv_line.price_unit # actual_sale["invoice_products"][str(inv_line.product_id.id)]["price_unit"] + inv_line.price_unit

                                    actual_sale["invoice_products"][str(inv_line.product_id.id)]["price_subtotal"] = actual_sale["invoice_products"][str(inv_line.product_id.id)]["price_subtotal"] + inv_line.price_subtotal

                                    actual_sale["invoice_products"][str(inv_line.product_id.id)]["price_total"] = actual_sale["invoice_products"][str(inv_line.product_id.id)]["price_total"] + inv_line.price_total
                                    #}

                                else:
                                    if inv_line.product_id.id:

                                        actual_sale["invoice_products"][str(inv_line.product_id.id)] = {
                                            "name": str(inv_line.product_id.name),
                                            "quantity": inv_line.quantity,
                                            "price_unit": inv_line.price_unit,
                                            "price_subtotal": inv_line.price_subtotal,
                                            "discount": 0,
                                            "tax": 0,
                                            "price_total": inv_line.price_total
                                        }


                        elif invoice.type == "out_refund":
                            if str(inv_line.product_id.id) in actual_sale["returned_products"]:
                                # actual_sale["returned_products"][str(inv_line.product_id.id)] = {
                                actual_sale["returned_products"][str(inv_line.product_id.id)]["quantity"] = actual_sale["returned_products"][str(inv_line.product_id.id)]["quantity"] + inv_line.quantity

                                actual_sale["returned_products"][str(inv_line.product_id.id)]["price_unit"] = inv_line.price_unit  #actual_sale["returned_products"][str(inv_line.product_id.id)]["price_unit"] + inv_line.price_unit

                                actual_sale["returned_products"][str(inv_line.product_id.id)]["price_subtotal"] = actual_sale["returned_products"][str(inv_line.product_id.id)]["price_subtotal"] + inv_line.price_subtotal

                                actual_sale["returned_products"][str(inv_line.product_id.id)]["price_total"] = actual_sale["returned_products"][str(inv_line.product_id.id)]["price_total"] + inv_line.price_total
                                #    }
                            else:
                                if inv_line.product_id.id:
                                    actual_sale["returned_products"][str(inv_line.product_id.id)] = {
                                        "name": str(inv_line.product_id.name),
                                        "quantity": inv_line.quantity,
                                        "price_unit": inv_line.price_unit,
                                        "price_subtotal": inv_line.price_subtotal,
                                        "discount": 0,
                                        "tax": 0,
                                        "price_total": inv_line.price_total
                                    }

                    # main products list preparation
                    if invoice.main_product_ids:
                        for main_product in invoice.main_product_ids:
                            main_product_d = {
                                "id": main_product.product.id,
                                "name": main_product.product.name,
                                "quantity": main_product.quantity
                            }
                            if main_product_d not in actual_sale["main_products"]:
                                actual_sale["main_products"].append(main_product_d)

                # --------------------------
                # Sales Discount - product fix
                all_product_name = []
                for product_id in actual_sale["actual_sale_products"]:
                    all_product_name.append(actual_sale["actual_sale_products"][product_id]["name"])
                if "Sales Discount" not in all_product_name:
                    for product_id in actual_sale["returned_products"]:
                        if actual_sale["returned_products"][product_id]["name"] == "Sales Discount":
                            actual_sale["actual_sale_products"][product_id] = {
                                "name": actual_sale["returned_products"][product_id]["name"],
                                "quantity": actual_sale["returned_products"][product_id]["quantity"],
                                "price_unit": actual_sale["returned_products"][product_id]["price_unit"],
                                "price_subtotal": actual_sale["returned_products"][product_id]["price_subtotal"],
                                "discount": 0,
                                "tax": 0,
                                "price_total": actual_sale["returned_products"][product_id]["price_total"]
                            }
                # --------------------------

                # prepare the actual_sale_products
                for product_id in actual_sale["invoice_products"]:
                    
                    # check if product_id exists in returned_products dictionary
                    if product_id in actual_sale["returned_products"]:

                        actual_sale["actual_sale_products"][product_id] = {
                            "name": actual_sale["invoice_products"][product_id]["name"],

                            "quantity": actual_sale["invoice_products"][product_id]["quantity"] - actual_sale["returned_products"][product_id]["quantity"],

                            "price_unit": actual_sale["invoice_products"][product_id]["price_unit"],

                            "price_subtotal": actual_sale["invoice_products"][product_id]["price_subtotal"] - actual_sale["returned_products"][product_id]["price_subtotal"],
                            "discount": 0,
                            "tax": 0,
                            "price_total": actual_sale["invoice_products"][product_id]["price_total"] - actual_sale["returned_products"][product_id]["price_total"]
                        }
                        """
                        
                        actual_sale["actual_sale_products"][product_id]['quantity'] = actual_sale["invoice_products"][product_id]["quantity"] - actual_sale["returned_products"][product_id]["quantity"]
                        # actual_sale["actual_sale_products"][product_id]['price_unit'] = actual_sale["invoice_products"][product_id]["price_unit"]
                        actual_sale["actual_sale_products"][product_id]['price_subtotal'] = actual_sale["invoice_products"][product_id]["price_subtotal"] - actual_sale["returned_products"][product_id]["price_subtotal"]
                        actual_sale["actual_sale_products"][product_id]['discount'] = 0
                        actual_sale["actual_sale_products"][product_id]['tax'] = 0
                        actual_sale["actual_sale_products"][product_id]['price_total'] = actual_sale["invoice_products"][product_id]["price_total"] - actual_sale["returned_products"][product_id]["price_total"]
                    """

                    else:

                        actual_sale["actual_sale_products"][product_id] = {

                            "name": actual_sale["invoice_products"][product_id]["name"],
                            "quantity": actual_sale["invoice_products"][product_id]["quantity"],
                            "price_unit":actual_sale["invoice_products"][product_id]["price_unit"],
                            "price_subtotal": actual_sale["invoice_products"][product_id]["price_subtotal"],
                            "discount": 0,
                            "tax": 0,
                            "price_total": actual_sale["invoice_products"][product_id]["price_total"]

                        }

                # invoice products list preparation
                if actual_sale["invoice_products"]:
                    for inv_product_id in actual_sale["invoice_products"]:
                        invoice_products_list.append({
                                "id": inv_product_id, 
                                "name": actual_sale["invoice_products"][inv_product_id]["name"], 
                                "quantity": actual_sale["invoice_products"][inv_product_id]["quantity"], 
                                "price_unit": actual_sale["invoice_products"][inv_product_id]["price_unit"], 
                                "price_subtotal": actual_sale["invoice_products"][inv_product_id]["price_subtotal"], 
                                "discount": 0,
                                "tax": 0,
                                "price_total": actual_sale["invoice_products"][inv_product_id]["price_total"]
                            })
                actual_sale["invoice_products_list"] = invoice_products_list


                # return products list preparation
                if actual_sale["returned_products"]:
                    for ret_product_id in actual_sale["returned_products"]:
                        returned_products_list.append({
                                "id": ret_product_id, 
                                "name": actual_sale["returned_products"][ret_product_id]["name"], 
                                "quantity": actual_sale["returned_products"][ret_product_id]["quantity"], 
                                "price_unit": actual_sale["returned_products"][ret_product_id]["price_unit"], 
                                "price_subtotal": actual_sale["returned_products"][ret_product_id]["price_subtotal"], 
                                "discount": 0,
                                "tax": 0,
                                "price_total": actual_sale["returned_products"][ret_product_id]["price_total"]
                            })
                actual_sale["returned_products_list"] = returned_products_list
                
                # actual sales products list preparation
                if actual_sale["actual_sale_products"]:
                    for act_product_id in actual_sale["actual_sale_products"]:
                        total_out_qty = actual_sale["invoice_products"][act_product_id]['quantity'] if act_product_id in actual_sale["invoice_products"] else 0

                        total_return_qty = actual_sale["returned_products"][act_product_id]['quantity'] if act_product_id in actual_sale["returned_products"] else 0
                        act_pr_name = actual_sale["actual_sale_products"][act_product_id]["name"]
                        prd_price_total = actual_sale["actual_sale_products"][act_product_id]["price_total"]
                        if act_pr_name == "Sales Discount" and prd_price_total > 0:
                            prd_price_total = prd_price_total * -1

                        actual_sale_products_list.append({
                                "id": act_product_id, 
                                "name": act_pr_name,
                                "out_qty": 1.0 if act_pr_name == "Sales Discount" else total_out_qty,
                                "return_qty": 0 if act_pr_name == "Sales Discount" else total_return_qty,
                                "delivered_quantity": 1.0 if act_pr_name == "Sales Discount" else actual_sale["actual_sale_products"][act_product_id]["quantity"],
                                "price_unit": actual_sale["actual_sale_products"][act_product_id]["price_unit"], 
                                "price_subtotal": actual_sale["actual_sale_products"][act_product_id]["price_subtotal"],
                                "discount": 0,
                                "tax": 0,
                                "price_total": prd_price_total
                            })
                # actual_sale_products_list.reverse()
                actual_sale["actual_sale_products_list"] = actual_sale_products_list

                # sales_data.append(actual_sale)
                data['result'] = actual_sale

            return {
                # 'doc_ids' : docids,
                # 'doc_model' : self.env['account.move'],
                # 'data' : data,
                # 'docs' : self.env['account.move'].browse(self.env.company.id),
                'docs': data,
            }

