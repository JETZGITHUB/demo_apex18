import json
from odoo import http
from odoo.http import request


class ZohoBookWebhook(http.Controller):
    def get_state_id(self, state):
        state_name = state.lower()
        if state_name == 'andhra pradesh':
            return 578
        elif state_name == 'arunachal pradesh':
            return 579
        elif state_name == 'assam':
            return 580
        elif state_name == 'bihar':
            return 581
        elif state_name == 'delhi':
            return 586
        elif state_name == 'goa':
            return 587
        elif state_name == 'gujarat':
            return 588
        elif state_name == 'karnataka':
            return 593
        elif state_name == 'kerala':
            return 594
        elif state_name == 'madhya':
            return 596
        elif state_name == 'maharastra':
            return 597
        elif state_name == 'puducherry':
            return 603
        elif state_name == 'punjab':
            return 604
        elif state_name == 'rajasthan':
            return 605
        elif state_name == 'tamilnadu':
            return 607
        elif state_name == 'uttar':
            return 610
        else:
            return 1384

    def get_gst_treatment(self, zoho_gst_treatment):
        if zoho_gst_treatment == 'business_gst':
            return 'regular'
        elif zoho_gst_treatment == 'overseas':
            return 'overseas'
        elif zoho_gst_treatment == 'consumer':
            return 'consumer'
        else:
            return 'unregistered'

    data = {'contact': {'owner_id': '', 'outstanding_ob_payable_amount': 0, 'outstanding_ob_receivable_amount': 0,
                        'can_show_vendor_ob_formatted': True, 'is_client_review_settings_enabled': False, 'pan_no': '',
                        'billing_address': {'zip': '', 'country': '', 'address': '', 'city': '',
                                            'address_id': '1465603000000043055', 'country_code': '', 'phone': '',
                                            'phone_formatted': '', 'attention': '', 'street2': '', 'state': '',
                                            'state_code': '', 'fax': ''},
                        'outstanding_receivable_amount_formatted': '₹0.00',
                        'source_formatted': 'User', 'is_credit_limit_migration_completed': False, 'language_code': 'en',
                        'twitter': '', 'unused_credits_receivable_amount_formatted': '₹0.00',
                        'unused_credits_receivable_amount_bcy': 0,
                        'unused_credits_receivable_amount_bcy_formatted': '₹0.00',
                        'outstanding_payable_amount_formatted': '₹0.00', 'entity_address_id': '1465603000000043060',
                        'pricebook_id': '', 'outstanding_receivable_amount': 0, 'exchange_rate': '',
                        'customer_sub_type': 'business', 'sales_channel': 'direct_sales',
                        'unused_credits_receivable_amount': 0, 'has_transaction': False, 'can_show_vendor_ob': True,
                        'opening_balance_amount_bcy_formatted': '', 'tags': [],
                        'unused_credits_payable_amount_formatted': '₹0.00', 'phone': '', 'company_name': '',
                        'is_consent_agreed': False, 'outstanding_receivable_amount_bcy_formatted': '₹0.00',
                        'crm_owner_id': '',
                        'status': 'active', 'opening_balance_amount_formatted': '₹0.00', 'zcrm_vendor_id': '',
                        'contact_category_formatted': '', 'currency_code': 'INR', 'outstanding_payable_amount': 0,
                        'unused_credits_payable_amount': 0, 'email': '', 'opening_balance_amount_bcy': '',
                        'contact_name': 'dhayalan rajarathnam', 'website': '',
                        'last_modified_time': '2023-09-26T10:57:51+0530', 'currency_symbol': '₹',
                        'ach_supported': False,
                        'facebook': '', 'last_name': '', 'contact_salutation': '', 'loyaltydetails': '',
                        'unused_retainer_payments_formatted': '₹0.00', 'opening_balances': [],
                        'payment_terms_label': 'Due on Receipt', 'is_crm_customer': False, 'addresses': [], 'notes': '',
                        'documents': [], 'credit_limit_exceeded_amount': 0, 'portal_status': 'disabled',
                        'is_linked_with_zohocrm': False,
                        'default_templates': {'salesorder_email_template_id': '', 'creditnote_email_template_id': '',
                                              'creditnote_template_name': '', 'paymentthankyou_email_template_name': '',
                                              'salesorder_template_name': '', 'invoice_email_template_name': '',
                                              'payment_remittance_email_template_name': '',
                                              'purchaseorder_template_name': '',
                                              'invoice_template_id': '', 'paymentthankyou_email_template_id': '',
                                              'bill_template_name': '', 'invoice_template_name': '',
                                              'bill_template_id': '',
                                              'purchaseorder_email_template_id': '', 'creditnote_template_id': '',
                                              'invoice_email_template_id': '', 'salesorder_template_id': '',
                                              'payment_remittance_email_template_id': '', 'estimate_template_id': '',
                                              'paymentthankyou_template_id': '', 'salesorder_email_template_name': '',
                                              'purchaseorder_template_id': '', 'creditnote_email_template_name': '',
                                              'purchaseorder_email_template_name': '', 'estimate_template_name': '',
                                              'estimate_email_template_id': '', 'paymentthankyou_template_name': '',
                                              'estimate_email_template_name': ''}, 'source': 'user',
                        'created_by_name': 'rdhayalan0306', 'outstanding_receivable_amount_bcy': 0, 'vpa_list': [],
                        'unused_credits_payable_amount_bcy_formatted': '₹0.00', 'trader_name': '',
                        'contact_category': '',
                        'allow_parent_for_payment_and_view': False, 'associated_with_square': False,
                        'contact_persons': [],
                        'created_time': '2023-09-26T10:47:23+0530', 'created_date_formatted': '26/09/2023',
                        'owner_name': '',
                        'custom_fields': [], 'credit_limit_exceeded_amount_formatted': '₹0.00',
                        'outstanding_payable_amount_bcy': 0, 'pricebook_name': '', 'price_precision': 2,
                        'primary_contact_id': '', 'checks': [], 'unused_credits_payable_amount_bcy': 0,
                        'vendor_currency_summaries': [
                            {'outstanding_payable_amount': 0, 'unused_credits_payable_amount_formatted': '₹0.00',
                             'currency_symbol': '₹', 'unused_credits_payable_amount': 0,
                             'outstanding_payable_amount_formatted': '₹0.00', 'is_base_currency': True,
                             'currency_name_formatted': 'INR- Indian Rupee', 'currency_id': '1465603000000000064',
                             'currency_code': 'INR', 'price_precision': 2}], 'designation': '', 'cards': [],
                        'can_show_customer_ob': True, 'can_show_customer_ob_formatted': True,
                        'contact_id': '1465603000000043053', 'payment_terms': 0, 'contact_type': 'vendor',
                        'is_sms_enabled': True, 'custom_field_hash': {}, 'legal_name': '',
                        'shipping_address': {'zip': '', 'country': '', 'address': '', 'city': '', 'latitude': '',
                                             'address_id': '1465603000000043057', 'country_code': '', 'phone': '',
                                             'phone_formatted': '', 'attention': '', 'street2': '', 'state': '',
                                             'state_code': '', 'fax': '', 'longitude': ''}, 'department': '',
                        'first_name': '',
                        'outstanding_ob_receivable_amount_formatted': '₹0.00', 'zohopeople_client_id': '',
                        'is_client_review_asked': False, 'customer_sub_type_formatted': 'Business',
                        'outstanding_payable_amount_bcy_formatted': '₹0.00', 'language_code_formatted': 'English',
                        'mobile': '', 'outstanding_ob_payable_amount_formatted': '₹0.00', 'unused_retainer_payments': 0,
                        'opening_balance_amount': 0, 'tds_tax_id': '', 'portal_receipt_count': 0,
                        'is_bcy_only_contact': True,
                        'consent_date': '', 'bank_accounts': [], 'created_date': '26/09/2023',
                        'currency_id': '1465603000000000064', 'payment_reminder_enabled': True}}

    @http.route('/zoho/vendor', type='json', auth='public', methods=['POST'], csrf=False)
    def webhook_vendor(self, *args, **kwargs):
        print('received webhook data vendors')
        # print("request", request.jsonrequest)
        data = json.loads(request.httprequest.data)
        vals = {
            'name': data['contact']['contact_name'],
            'contact_type': 'vendor',
            'type': 'contact',
            'street': data['contact']['billing_address']['address'],
            'street2': data['contact']['billing_address']['street2'],
            'city': data['contact']['billing_address']['city'],
            'zip': data['contact']['billing_address']['zip'],
            'zoho_id': data['contact']['contact_id'],
            'is_zoho': True,
            'l10n_in_gst_treatment': self.get_gst_treatment(data['contact']['gst_treatment']),
            'vat': data['contact']['gst_no'],
            'mobile': data['contact']['mobile'],
            'email': data['contact']['email'],
            'country_id': 104,
            'state_id': self.get_state_id(data['contact']['billing_address']['state']),
        }
        # print("valseh", vals)

        vendors = http.request.env['res.partner'].sudo().search([('zoho_id', '!=', False)])
        vendor_zoho_id_list = []
        for rec in vendors:
            vendor_zoho_id_list.append(rec.zoho_id)
        # print("zoho id list of vendors in odoo", vendor_zoho_id_list)
        if vals['zoho_id'] in vendor_zoho_id_list:
            # print("zoho id andha list kulla irukku, write")
            existing_vendor = http.request.env['res.partner'].sudo().search([('zoho_id', '=', vals['zoho_id'])])
            existing_vendor.write(vals)

        else:
            print("ila adhunala create")
            http.request.env['res.partner'].sudo().create(vals)
        # print('data', data)
        print("completed the webhook vendor")
        return {'type': 'ir.actions.act_close_wizard_and_reload_view'}

    @http.route('/zoho/item', type='json', auth='public', methods=['post'], csrf=False)
    def webhook_item(self, *args, **kwargs):
        print("called webhook item")
        data = json.loads(request.httprequest.data)
        print('data', data)
        products = http.request.env['product.template'].sudo().search([])
        default_code_list = []
        for rec in products:
            default_code_list.append(rec.default_code)
        if data['item']['name'] in default_code_list:
            existing_product = http.request.env['product.template'].sudo().search(
                [('default_code', '=', data['item']['name'])])
            item_type = data['item']['item_type']
            if item_type == 'purchases' or item_type == 'sales_and_purchases':
                existing_product.write({'zoho_id': data['item']['item_id'],
                                        'is_zoho': True})
            else:
                print("halla mithi habi boo halla mithi habi vandhaley halla mithi habbi boo")
                pass
        print("completed webhook item")

    data = {'purchaseorder': {'can_send_in_mail': False, 'discount': 0, 'taxes': [], 'delivery_customer_address_id': '',
                              'billing_address': {'zip': '', 'country': '', 'address': '', 'city': '', 'phone': '',
                                                  'attention': '', 'street2': '', 'state': '', 'fax': ''},
                              'total_quantity_formatted': '20.00', 'line_items': [
            {'bcy_rate': 10, 'item_total_formatted': '₹100.00', 'salesorder_item_id': '',
             'line_item_id': '1400557000000049220', 'rate_formatted': '₹10.00', 'header_id': '',
             'item_type': 'sales_and_purchases', 'item_type_formatted': 'Sales and Purchase Items', 'description': '',
             'discount': 0, 'quantity_cancelled': 0, 'gst_treatment_code': '', 'item_order': 1, 'image_name': '',
             'discounts': [], 'rate': 10, 'project_id': '', 'account_name': 'Cost of Goods Sold',
             'hsn_or_sac': '852963', 'sku': '888999000', 'quantity_billed': 0, 'pricebook_id': '', 'image_type': '',
             'tax_exemption_code': '', 'bcy_rate_formatted': '₹10.00', 'image_document_id': '', 'quantity': 10,
             'item_id': '1400557000000049137', 'reverse_charge_tax_id': '', 'tax_name': '', 'item_total': 100,
             'header_name': '', 'item_custom_fields': [], 'tax_exemption_id': '', 'tax_id': '', 'line_item_taxes': [],
             'tags': [], 'unit': 'ft', 'account_id': '1400557000000000567', 'product_type': 'goods', 'tax_type': 'tax',
             'name': 'biscuite', 'tax_percentage': 0, 'purchase_request_items': []},
            {'bcy_rate': 22000, 'item_total_formatted': '₹2,20,000.00', 'salesorder_item_id': '',
             'line_item_id': '1400557000000049222', 'rate_formatted': '₹22,000.00', 'header_id': '',
             'item_type': 'sales_and_purchases', 'item_type_formatted': 'Sales and Purchase Items', 'description': '',
             'discount': 0, 'quantity_cancelled': 0, 'gst_treatment_code': '', 'item_order': 2, 'image_name': '',
             'discounts': [], 'rate': 22000, 'project_id': '', 'account_name': 'Cost of Goods Sold', 'hsn_or_sac': '',
             'sku': '', 'quantity_billed': 0, 'pricebook_id': '', 'image_type': '', 'tax_exemption_code': '',
             'bcy_rate_formatted': '₹22,000.00', 'image_document_id': '', 'quantity': 10,
             'item_id': '1400557000000049170', 'reverse_charge_tax_id': '', 'tax_name': '', 'item_total': 220000,
             'header_name': '', 'item_custom_fields': [], 'tax_exemption_id': '', 'tax_id': '', 'line_item_taxes': [],
             'tags': [], 'unit': 'dz', 'account_id': '1400557000000000567', 'product_type': 'goods', 'tax_type': 'tax',
             'name': '996633', 'tax_percentage': 0, 'purchase_request_items': []}], 'submitted_by_email': '',
                              'order_status': 'open', 'gst_no': '', 'terms': '', 'can_mark_as_bill': False,
                              'total_quantity': 20, 'has_qty_cancelled': False, 'sub_total_inclusive_of_tax': 0,
                              'delivery_customer_id': '', 'exchange_rate': 1, 'approver_id': '',
                              'submitted_date_formatted': '', 'status_formatted': 'Open', 'reference_number': '',
                              'vendor_id': '1400557000000016436', 'tax_treatment_formatted': 'Unregistered Business',
                              'is_pre_gst': False, 'page_height': '11.69in', 'status': 'open', 'tax_total': 0,
                              'is_viewed_by_client': False, 'source_of_supply_formatted': 'Arunachal Pradesh',
                              'adjustment_formatted': '₹0.00', 'purchaseorder_id': '1400557000000049217',
                              'discount_account_id': '', 'currency_code': 'INR', 'page_width': '8.27in',
                              'sub_statuses': [], 'date_formatted': '23/09/2023', 'destination_of_supply': 'TN',
                              'client_viewed_time_formatted': '', 'tax_rounding': 'entity_level', 'salesorders': [],
                              'adjustment_description': 'Adjustment', 'last_modified_time': '2023-09-23T18:54:06+0530',
                              'currency_symbol': '₹', 'gst_treatment_formatted': 'Unregistered Business',
                              'discount_type': 'entity_level', 'is_adv_tracking_in_receive': False,
                              'tax_override': False, 'purchaseorder_number': 'PO-00001', 'template_name': '',
                              'delivery_date_formatted': '30/09/2023', 'source_of_supply': 'AR',
                              'template_id': '1400557000000000237', 'can_mark_as_unbill': False,
                              'total_formatted': '₹2,20,100.00', 'is_reverse_charge_applied': False,
                              'payment_terms_label': 'Due on Receipt', 'date': '2023-09-23', 'submitted_date': '',
                              'delivery_address': {'zip': '', 'country': 'India', 'address': '', 'is_verifiable': True,
                                                   'is_primary': True, 'address2': '', 'city': '', 'address1': '',
                                                   'is_verified': False,
                                                   'organization_address_id': '1400557000000016194', 'phone': '',
                                                   'is_valid': False, 'state': 'Tamil Nadu',
                                                   'email': 'kavalayya@outlook.com'}, 'notes': '',
                              'template_type_formatted': 'Standard', 'documents': [], 'client_viewed_time': '',
                              'discount_amount': 0, 'order_status_formatted': 'Issued', 'billed_status_formatted': '',
                              'contact_category': 'business_none', 'template_type': 'standard', 'color_code': '',
                              'contact_persons': [], 'billing_address_id': '1400557000000016438',
                              'gst_treatment': 'business_none', 'created_time': '2023-09-23T15:12:56+0530',
                              'is_inclusive_tax': False, 'custom_fields': [], 'ship_via_id': '',
                              'vendor_name': 'house owner', 'discount_applied_on_amount_formatted': '₹0.00',
                              'price_precision': 2, 'delivery_date': '2023-09-30',
                              'sub_total_inclusive_of_tax_formatted': '₹0.00', 'submitted_by_photo_url': '',
                              'tax_treatment': 'business_none', 'current_sub_status_formatted': 'Issued',
                              'approvers_list': [], 'ship_via': '', 'adjustment': 0, 'submitted_by_name': '',
                              'created_by_id': '1400557000000016001', 'current_sub_status': 'open',
                              'discount_amount_formatted': '₹0.00', 'destination_of_supply_formatted': 'Tamil Nadu',
                              'delivery_org_address_id': '1400557000000016194', 'billed_status': '',
                              'is_discount_before_tax': True, 'attachment_name': '', 'expected_delivery_date': '',
                              'payment_terms': 0, 'total': 220100, 'expected_delivery_date_formatted': '',
                              'tax_total_formatted': '₹0.00', 'current_sub_status_id': '',
                              'sub_total_formatted': '₹2,20,100.00', 'custom_field_hash': {}, 'bills': [],
                              'orientation': 'portrait', 'discount_applied_on_amount': 0, 'submitted_by': '',
                              'submitter_id': '', 'is_emailed': True, 'sub_total': 220100, 'attention': 'kavalayya',
                              'currency_id': '1400557000000000064'}}

    def get_partner_id(self, zoho_id):
        partner = http.request.env['res.partner'].sudo().search([('zoho_id', '=', zoho_id)])
        return partner.id

    def get_product(self, zoho_id):
        product = http.request.env['product.template'].sudo().search([('zoho_id', '=', zoho_id)])
        return {'id': product.id,
                'conversion': product.uom_value,
                'purchase_unit_id': product.uom_po_id.id}

    zoho_line_items = [{'bcy_rate': 10, 'item_total_formatted': '₹300.00', 'salesorder_item_id': '',
                        'line_item_id': '1400557000000049220', 'rate_formatted': '₹10.00', 'header_id': '',
                        'item_type': 'sales_and_purchases', 'item_type_formatted': 'Sales and Purchase Items',
                        'description': '', 'discount': 0, 'quantity_cancelled': 0, 'gst_treatment_code': '',
                        'item_order': 1, 'image_name': '', 'discounts': [], 'rate': 10, 'project_id': '',
                        'account_name': 'Cost of Goods Sold', 'hsn_or_sac': '852963', 'sku': '888999000',
                        'quantity_billed': 0, 'pricebook_id': '', 'image_type': '', 'tax_exemption_code': '',
                        'bcy_rate_formatted': '₹10.00', 'image_document_id': '', 'quantity': 30,
                        'item_id': '1400557000000049137', 'reverse_charge_tax_id': '', 'tax_name': '',
                        'item_total': 300,
                        'header_name': '', 'item_custom_fields': [], 'tax_exemption_id': '', 'tax_id': '',
                        'line_item_taxes': [], 'tags': [], 'unit': 'ft', 'account_id': '1400557000000000567',
                        'product_type': 'goods', 'tax_type': 'tax', 'name': 'biscuite', 'tax_percentage': 0,
                        'purchase_request_items': []},

                       {'bcy_rate': 22000, 'item_total_formatted': '₹11,00,000.00',
                        'salesorder_item_id': '', 'line_item_id': '1400557000000049222',
                        'rate_formatted': '₹22,000.00', 'header_id': '',
                        'item_type': 'sales_and_purchases',
                        'item_type_formatted': 'Sales and Purchase Items',
                        'description': '', 'discount': 0, 'quantity_cancelled': 0,
                        'gst_treatment_code': '', 'item_order': 2, 'image_name': '',
                        'discounts': [], 'rate': 22000, 'project_id': '',
                        'account_name': 'Cost of Goods Sold', 'hsn_or_sac': '', 'sku': '',
                        'quantity_billed': 0, 'pricebook_id': '', 'image_type': '',
                        'tax_exemption_code': '', 'bcy_rate_formatted': '₹22,000.00',
                        'image_document_id': '', 'quantity': 50,
                        'item_id': '1400557000000049170', 'reverse_charge_tax_id': '',
                        'tax_name': '', 'item_total': 1100000, 'header_name': '',
                        'item_custom_fields': [], 'tax_exemption_id': '', 'tax_id': '',
                        'line_item_taxes': [], 'tags': [], 'unit': 'dz',
                        'account_id': '1400557000000000567', 'product_type': 'goods',
                        'tax_type': 'tax', 'name': '996633', 'tax_percentage': 0,
                        'purchase_request_items': []}]
    odoo_lineitem_id_list = [1931, 1932]

    def update_line_items(self, zoho_line_items, odoo_lineitem_id_list):
        odoo_items_zoho_id_list = []
        products = http.request.env['product.template'].sudo().search([('zoho_id', '!=', False)])
        for item in products:
            odoo_items_zoho_id_list.append(item.zoho_id)
        if len(zoho_line_items) == len(odoo_lineitem_id_list):
            line_items = []
            index = 0
            for zo_item in zoho_line_items:
                print("enann item id ippo update aaga pogudhu", odoo_lineitem_id_list[index])
                if zo_item['item_id'] not in odoo_items_zoho_id_list:
                    return False
                else:
                    product = self.get_product(zo_item['item_id'])
                    product_id = product['id']
                    conversion = product['conversion'] if product['conversion'] != 0 else 1
                    purchase_unit_id = product['purchase_unit_id']
                    product_qty = float(zo_item['quantity']) * conversion
                    price_unit = float(zo_item['rate']) / conversion
                    line_vals = {
                        'product_id': product_id,
                        'name': zo_item['name'],
                        'std_quantity': zo_item['quantity'],
                        'std_unit_price': zo_item['rate'],
                        'ordered_qty': f"{zo_item['quantity']} {zo_item['unit']}",
                        'uom_line_value': conversion,
                        'product_qty': product_qty,
                        'product_uom': purchase_unit_id,
                        'price_unit': price_unit
                    }
                    line_items.append((1, odoo_lineitem_id_list[index], line_vals))
                    index += 1
            return line_items
        else:
            # TODO ADD LOGIC TO HANDLE PURCHASE ORDER WHERE LINE ITEMS ARE ADDED OR REMOVED
            return False

    def get_line_items(self, zoho_line_items):
        odoo_items_zoho_id_list = []
        products = http.request.env['product.template'].sudo().search([('zoho_id', '!=', False)])
        for item in products:
            odoo_items_zoho_id_list.append(item.zoho_id)

        line_items = []
        for zo_item in zoho_line_items:
            if zo_item['item_id'] not in odoo_items_zoho_id_list:
                return 'skip'
            else:
                product = self.get_product(zo_item['item_id'])
                product_id = product['id']
                conversion = product['conversion'] if product['conversion'] != 0 else 1
                purchase_unit_id = product['purchase_unit_id']
                product_qty = float(zo_item['quantity']) * conversion
                price_unit = float(zo_item['rate']) / conversion
                line_vals = {
                    'product_id': product_id,
                    'name': zo_item['name'],
                    'std_quantity': zo_item['quantity'],
                    'std_unit_price': zo_item['rate'],
                    'ordered_qty': f"{zo_item['quantity']} {zo_item['unit']}",
                    'uom_line_value': conversion,
                    'product_qty': product_qty,
                    'product_uom': purchase_unit_id,
                    'price_unit': price_unit
                }
                line_items.append((0, 0, line_vals))
        return line_items

    def format_datetime(self, zoho_date):
        from datetime import datetime
        if zoho_date != '':
            date_time = datetime.strptime(zoho_date, "%Y-%m-%d")
            return date_time
        else:
            return False

    @http.route('/zoho/po', type='json', auth='public', methods=['post'], csrf=False)
    def webhook_po(self, *args, **kwargs):
        print("called webhook po")
        data = json.loads(request.httprequest.data)
        vals = {
            'name': data['purchaseorder']['purchaseorder_number'],
            'partner_id': self.get_partner_id(data['purchaseorder']['vendor_id']),
            'zoho_id': data['purchaseorder']['purchaseorder_id'],
            'is_zoho': True,
            'l10n_in_gst_treatment': self.get_gst_treatment(data['purchaseorder']['gst_treatment']),
            'date_approve': self.format_datetime(zoho_date=data['purchaseorder']['date']),
            'date_planned': self.format_datetime(zoho_date=data['purchaseorder']['delivery_date']),
            'order_line': self.get_line_items(data['purchaseorder']['line_items'])
        }
        po_s = http.request.env['purchase.order'].sudo().search([('zoho_id', '!=', False)])
        po_zoho_id_list = []
        for po in po_s:
            po_zoho_id_list.append(po.zoho_id)
        if vals['order_line'] == 'skip':
            pass
        elif vals['zoho_id'] in po_zoho_id_list:
            existing_po = http.request.env['purchase.order'].sudo().search([('zoho_id', '=', vals['zoho_id'])])
            order_lineitems_id_list = []
            for item in existing_po.order_line:
                order_lineitems_id_list.append(item.id)
            line_items = self.update_line_items(data['purchaseorder']['line_items'], order_lineitems_id_list)
            if line_items is False:
                del vals['order_line']
            else:
                vals['order_line'] = line_items
            existing_po.write(vals)
        else:
            created_po = http.request.env['purchase.order'].sudo().create(vals)
            created_po.button_confirm()
            origin = created_po.name
            transfer = http.request.env['stock.picking'].sudo().search([('origin', '=', origin)])
            for line in transfer.move_ids_without_package:
                line.ordered_qty = line.purchase_line_id.ordered_qty
                line.uom_line_value = line.product_id.uom_value if line.product_id.uom_value != 0 else 1

        print('data', data)
