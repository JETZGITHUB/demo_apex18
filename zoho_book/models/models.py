from odoo import models, fields, api, _
import requests
import logging
import json
from odoo.exceptions import ValidationError, UserError
# from odoo.exceptions import UserError
# import http.client
# import schedule
import re
from datetime import datetime, date, timedelta, time
import decimal

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_round, get_lang

_logger = logging.getLogger(__name__)

# ******************************************* CODE CREATED BY jagadishmagesh1999@gmail.com *************************************************************#
# ******************************************* CODE EDITED BY kumaru kokki kumaru *************************************************************#

ZOHO_PO_STATUS = 'open'
DATE = date.today()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_po_name = fields.Char(string="PO NO")


class UnwantedPo(models.Model):
    _name = 'unwanted.po'

    po_num = fields.Char("PO NUMBER")
    zoho_id = fields.Char(string='Zoho ID', copy=False, readonly=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    zoho_id = fields.Char(string='Zoho ID', copy=False, readonly=True)
    is_zoho = fields.Boolean(string='Is Zoho')
    contact_type = fields.Selection([('customer', 'Customer'), ('vendor', 'vendor')], string="Contact Type",
                                    default="customer")
    company_type = fields.Selection([('company', 'business'), ('person', 'individual')],
                                    compute='_compute_company_type', inverse='_write_company_type')

    def import_contacts(self):
        print("pandassuma pandassuma")
        self.env['zoho.books'].import_contacts_zoho()
        return


class Items(models.Model):
    _inherit = 'product.template'

    zoho_id = fields.Char("Zoho ID", copy=False)
    is_zoho = fields.Boolean("Zoho ?")
    uom_value = fields.Float(digits=(12, 6), string="Value", default=1)

    def import_products(self):
        print("pandassuma pandassuma")
        self.env['zoho.books'].import_items_zoho()
        return


class StockMove(models.Model):
    _inherit = 'stock.move'

    ordered_qty = fields.Char("Ordered Qty", related='purchase_line_id.ordered_qty')
    # uom_line_value = fields.Float(digits=(12, 6), string="Conversion value", states={'done': [('readonly', True)]})
    # std_quantity = fields.Float("Ordered Qty")
    # product_uom_qty = fields.Float(required=True, digits=(12, 6),
    #                                compute="compute_product_uom_qty", inverse='inverse_product_uom_qty', store=True)
    # # uom_stock_qty = fields.Float(related='purchase_line_id.uom_qty', store=True, digits=(12, 6))
    # change_actual_qty = fields.Boolean()
    # reserved_availability = fields.Float(compute='_compute_reserved_availability',
    #                                      inverse='inverse_reserved_availability', digits=(12, 6))
    # change_reserved = fields.Boolean()
    # quantity_done = fields.Float(digits=(12, 6))
    # manual_uom_qty = fields.Float(digits=(12, 6), string="manual uom_qty")
    uom_stock_qty = fields.Float( store=True,
                                 digits=(12, 6))
    # change_uom_stock_qty = fields.Boolean()

    # @api.depends('purchase_line_id.uom_qty', 'change_uom_stock_qty')
    # def compute_uom_stock_qty(self):
    #     for line in self:
    #         if line.to_refund:
    #             line.uom_stock_qty = line.manual_uom_qty
    #         else:
    #             line.uom_stock_qty = line.purchase_line_id.uom_qty
    #
    # @api.depends('uom_stock_qty')
    # def inverse_of_uom_stock_qty(self):
    #     for line in self:
    #         line.manual_uom_qty = line.uom_stock_qty

    # @api.onchange('uom_line_value')
    # def onchange_uom_line_value(self):
    #     self.quantity_done = 0
    #     zoho_unit = self.ordered_qty
    #     if zoho_unit:
    #         for i in "0123456789.":
    #             if i in zoho_unit:
    #                 zoho_unit = zoho_unit.replace(i, "")
    #
    #     is_same = check_same_units(zoho_unit=zoho_unit, odoo_unit=self.purchase_line_id.product_id.uom_po_id.name)
    #     if self.uom_line_value and self.ordered_qty != 0 and is_same is False:
    #         self.purchase_line_id.price_unit = (self.purchase_line_id.std_unit_price / self.uom_line_value)
    #         self.purchase_line_id.uom_line_value = self.uom_line_value
    #     else:
    #         self.purchase_line_id.uom_line_value = 1
    #         self.uom_line_value = 1

    # @api.depends('uom_line_value', 'change_actual_qty', 'uom_stock_qty')
    # def compute_product_uom_qty(self):
    #     for line in self:
    #         if line.state == 'done' and line.quantity_done == 0:
    #             line.product_uom_qty = 0
    #         elif line.change_actual_qty and line.quantity_done != 0:
    #             line.product_uom_qty = line.quantity_done
    #             line.change_reserved = True
    #         else:
    #             if line.uom_stock_qty != 0:
    #                 line.product_uom_qty = line.uom_stock_qty
    #                 line.change_reserved = True

    # @api.onchange('product_uom_qty')
    # def inverse_product_uom_qty(self):
    #     # self.env.context.get('active_model')
    #     # print("self", self, "+++", self.env.context)
    #     # active_model = self.env.context.get('active_model')
    #     # if active_model == 'stock.picking':
    #     #     print("active_model picking True")
    #     for line in self:
    #         line.change_actual_qty = True

    # @api.depends('move_line_ids.product_qty')
    # def _compute_reserved_availability(self):
    #     """ Fill the `availability` field on a stock move, which is the actual reserved quantity
    #     and is represented by the aggregated `product_qty` on the linked move lines. If the move
    #     is force assigned, the value will be 0.
    #     """
    #     if not any(self._ids):
    #         # onchange
    #         for move in self:
    #             reserved_availability = sum(move.move_line_ids.mapped('product_qty'))
    #             move.reserved_availability = move.product_id.uom_id._compute_quantity(
    #                 reserved_availability, move.product_uom, rounding_method='HALF-UP')
    #     else:
    #         # compute
    #         result = {data['move_id'][0]: data['product_qty'] for data in
    #                   self.env['stock.move.line'].read_group([('move_id', 'in', self.ids)], ['move_id', 'product_qty'],
    #                                                          ['move_id'])}
    #         for move in self:
    #             if move.change_reserved:
    #                 move.reserved_availability = move.product_uom_qty
    #             else:
    #                 # move.reserved_availability = move.product_uom_qty
    #                 move.reserved_availability = move.product_id.uom_id._compute_quantity(
    #                     result.get(move.id, 0.0), move.product_uom, rounding_method='HALF-UP')
    #
    # def inverse_reserved_availability(self):
    #     print("zoho_book--models--inverse_reserved_availability??????????")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    ordered_qty = fields.Char("Ordered Qty", readonly=True)
    zoho_total_price = fields.Float()
    is_zoho = fields.Boolean()

    @api.depends('product_qty', 'product_uom', 'company_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            print("................ratata", line.zoho_total_price)
            if line.zoho_total_price == 0:
                if not line.product_id or line.invoice_lines or not line.company_id:
                    continue
                params = {'order_id': line.order_id}
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(line),
                    uom_id=line.product_uom,
                    params=params)

                if seller or not line.date_planned:
                    line.date_planned = line._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

                # If not seller, use the standard price. It needs a proper currency conversion.
                if not seller:
                    unavailable_seller = line.product_id.seller_ids.filtered(
                        lambda s: s.partner_id == line.order_id.partner_id)
                    if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom:
                        # Avoid to modify the price unit if there is no price list for this partner and
                        # the line has already one to avoid to override unit price set manually.
                        continue
                    po_line_uom = line.product_uom or line.product_id.uom_po_id
                    price_unit = line.env['account.tax']._fix_tax_included_price_company(
                        line.product_id.uom_id._compute_price(line.product_id.standard_price, po_line_uom),
                        line.product_id.supplier_taxes_id,
                        line.taxes_id,
                        line.company_id,
                    )
                    price_unit = line.product_id.cost_currency_id._convert(
                        price_unit,
                        line.currency_id,
                        line.company_id,
                        line.date_order or fields.Date.context_today(line),
                        False
                    )
                    line.price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                                   self.env[
                                                                                       'decimal.precision'].precision_get(
                                                                                       'Product Price')))
                    continue

                price_unit = line.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                                     line.product_id.supplier_taxes_id,
                                                                                     line.taxes_id,
                                                                                     line.company_id) if seller else 0.0
                price_unit = seller.currency_id._convert(price_unit, line.currency_id, line.company_id,
                                                         line.date_order or fields.Date.context_today(line), False)
                price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                          self.env['decimal.precision'].precision_get(
                                                                              'Product Price')))
                line.price_unit = seller.product_uom._compute_price(price_unit, line.product_uom)
                line.discount = seller.discount or 0.0

                # record product names to avoid resetting custom descriptions
                default_names = []
                vendors = line.product_id._prepare_sellers({})
                product_ctx = {'seller_id': None, 'partner_id': None, 'lang': get_lang(line.env, line.partner_id.lang).code}
                default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
                for vendor in vendors:
                    product_ctx = {'seller_id': vendor.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                    default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
                if not line.name or line.name in default_names:
                    product_ctx = {'seller_id': seller.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                    line.name = line._get_product_purchase_description(line.product_id.with_context(product_ctx))

            else:
                if not line.product_id or line.invoice_lines or not line.company_id:
                    continue
                params = {'order_id': line.order_id}
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(
                        line),
                    uom_id=line.product_uom,
                    params=params)

                if seller or not line.date_planned:
                    line.date_planned = line._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

                # If not seller, use the standard price. It needs a proper currency conversion.
                if not seller:
                    unavailable_seller = line.product_id.seller_ids.filtered(
                        lambda s: s.partner_id == line.order_id.partner_id)
                    if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom:
                        # Avoid to modify the price unit if there is no price list for this partner and
                        # the line has already one to avoid to override unit price set manually.
                        continue
                    price_unit = line.zoho_total_price/line.product_qty
                    line.price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                                   self.env[
                                                                                       'decimal.precision'].precision_get(
                                                                                       'Product Price')))
                    continue

                price_unit = line.zoho_total_price / line.product_qty
                price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                          self.env['decimal.precision'].precision_get(
                                                                              'Product Price')))
                line.price_unit = seller.product_uom._compute_price(price_unit, line.product_uom)
                line.discount = seller.discount or 0.0

                # record product names to avoid resetting custom descriptions
                default_names = []
                vendors = line.product_id._prepare_sellers({})
                product_ctx = {'seller_id': None, 'partner_id': None,
                               'lang': get_lang(line.env, line.partner_id.lang).code}
                default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
                for vendor in vendors:
                    product_ctx = {'seller_id': vendor.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                    default_names.append(
                        line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
                if not line.name or line.name in default_names:
                    product_ctx = {'seller_id': seller.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                    line.name = line._get_product_purchase_description(line.product_id.with_context(product_ctx))


class IrCron(models.Model):
    _inherit = 'ir.cron'

    is_zoho = fields.Boolean("Zoho ?")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_po_name = fields.Char(string="PO NO")

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    zoho_id = fields.Char("Zoho PurchaseOrder ID", copy=False)
    is_zoho = fields.Boolean("Zoho ?")
    company_id = fields.Many2one("res.company")
    partner_id = fields.Many2one(required=False)
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Need To Receive'),
        ('partial', 'Partially Received'),
        ('complete_receive', 'Completed'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def change_status(self, po_num, partial=False):
        po = self.env['purchase.order'].search([('name', '=', po_num)])
        if partial is False:
            po.state = 'complete_receive'
        else:
            po.state = 'partial'

    def import_pos(self):
        self.env['zoho.books'].import_purchase_zoho()
        print("its the way down we go,")
        return

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
    #     print('i am field view get method in purchase.order form in zoho_book man iam also called')
    #     res = super(PurchaseOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                      submenu=submenu)
    #     print(res)
    #     self.compute_received_and_actual_sum()
    #     return res


def check_same_units(zoho_unit, odoo_unit):
    zoho_unit_to_odoo = {
        'BOX': 'Units',
        'FEET': 'ft',
        'INCHES': 'in',
        'KGS': 'kg',
        'LTR': 'L',
        'MTR': 'm',
        'PCS': 'Units',
        'NOS': 'Units',
        'ROLLS': 'rolls',
        '': 'Units'
    }
    for key in zoho_unit_to_odoo:
        if key == zoho_unit:
            zoho_unit = zoho_unit_to_odoo[key]

    if zoho_unit == odoo_unit:
        return True
    else:
        return False


class ZohoBooks(models.Model):
    _name = 'zoho.books'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'organization_id'

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.user.company_id.id)
    organization_id = fields.Char("Organization ID", required=True)
    client_id = fields.Char("Client ID", required=True)
    client_secrete = fields.Char("Client Secrete", required=True)
    code = fields.Char(tracking=True)
    refresh_token = fields.Char(tracking=True)
    zoho_token = fields.Char(tracking=True)
    state = fields.Selection([
        ('in', 'India'),
        ('com', 'United States'),
        ('eu', 'Europe'),
        ('jp', 'Japan'),
        ('com.au', 'Australia'),
    ], default='in', string='Region')
    auto_sign = fields.Boolean("Auto Access Token", tracking=True)
    auto_import_items = fields.Boolean("Auto Import Items", tracking=True)
    auto_import_contacts = fields.Boolean("Auto Import Contacts", tracking=True)

    def custom_function(self):
        pos = self.env['purchase.order'].search([])
        for po in pos:
            actual_sum = sum(po.order_line.mapped('product_qty'))
            received_sum = sum(po.order_line.mapped('qty_received'))
            separation_date = datetime(2023, 12, 1)
            print("date order", po.date_order, type(po.date_order))
            if po.date_order < separation_date:
                if received_sum == 0:
                    po.state = 'purchase'
                elif actual_sum > received_sum:
                    po.state = 'partial'
                elif actual_sum == received_sum:
                    po.state = 'done'

    def zoho_code_generate(self):
        base_url = "https://www.zohoapis.com/books/v3/items"  # Default URL
        if self.state == 'in':
            base_url = "https://accounts.zoho.in/oauth/v2/auth"
        elif self.state == 'com':
            base_url = "https://accounts.zoho.com/oauth/v2/auth"
        elif self.state == 'eu':
            base_url = "https://accounts.zoho.eu/oauth/v2/auth"
        elif self.state == 'jp':
            base_url = "https://accounts.zoho.jp/oauth/v2/auth"
        elif self.state == 'com.au':
            base_url = "https://accounts.zoho.com.au/oauth/v2/auth"

        url = f"{base_url}?response_type=code&client_id={self.client_id}&scope=ZohoBooks.contacts.Create,ZohoBooks.contacts.UPDATE,ZohoBooks.contacts.READ,ZohoBooks.contacts.DELETE,ZohoBooks.settings.Create,ZohoBooks.settings.UPDATE,ZohoBooks.settings.READ,ZohoBooks.settings.DELETE,ZohoBooks.estimates.Create,ZohoBooks.estimates.UPDATE,ZohoBooks.estimates.READ,ZohoBooks.estimates.DELETE,ZohoBooks.accountants.Create,ZohoBooks.accountants.UPDATE,ZohoBooks.accountants.READ,ZohoBooks.accountants.DELETE,ZohoBooks.banking.Create,ZohoBooks.banking.UPDATE,ZohoBooks.banking.READ,ZohoBooks.banking.DELETE,ZohoBooks.vendorpayments.Create,ZohoBooks.vendorpayments.UPDATE,ZohoBooks.vendorpayments.READ,ZohoBooks.vendorpayments.DELETE,ZohoBooks.debitnotes.Create,ZohoBooks.debitnotes.UPDATE,ZohoBooks.debitnotes.READ,ZohoBooks.debitnotes.DELETE,ZohoBooks.bills.Create,ZohoBooks.bills.UPDATE,ZohoBooks.bills.READ,ZohoBooks.bills.DELETE,ZohoBooks.purchaseorders.Create,ZohoBooks.purchaseorders.UPDATE,ZohoBooks.purchaseorders.READ,ZohoBooks.purchaseorders.DELETE,ZohoBooks.salesorders.Create,ZohoBooks.salesorders.UPDATE,ZohoBooks.salesorders.READ,ZohoBooks.salesorders.DELETE,ZohoBooks.expenses.Create,ZohoBooks.expenses.UPDATE,ZohoBooks.expenses.READ,ZohoBooks.expenses.DELETE,ZohoBooks.customerpayments.Create,ZohoBooks.customerpayments.UPDATE,ZohoBooks.customerpayments.READ,ZohoBooks.customerpayments.DELETE,ZohoBooks.invoices.Create,ZohoBooks.invoices.UPDATE,ZohoBooks.invoices.READ,ZohoBooks.invoices.DELETE&redirect_uri=https://www.mi.com/&access_type=offline"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
            'res_id': self.id,
        }

    def zoho_refresh_token_generate(self):
        base_url = "https://accounts.zoho.in/oauth/v2/token"  # Default URL
        if self.state == 'in':
            base_url = "https://accounts.zoho.in/oauth/v2/token"
        elif self.state == 'com':
            base_url = "https://accounts.zoho.com/oauth/v2/token"
        elif self.state == 'eu':
            base_url = "https://accounts.zoho.eu/oauth/v2/token"
        elif self.state == 'jp':
            base_url = "https://accounts.zoho.jp/oauth/v2/token"
        elif self.state == 'com.au':
            base_url = "https://accounts.zoho.com.au/oauth/v2/token"

        url = f"{base_url}?grant_type=authorization_code&client_id={self.client_id}&client_secret={self.client_secrete}&redirect_uri=https://www.mi.com/&code={self.code}"
        response = requests.post(url)

        if response.status_code == 200:
            decoded = json.loads(response.text)
            refresh_token = decoded.get('refresh_token')
            self.write({'refresh_token': refresh_token})

    def zoho_authtoken_generate(self):
        base_url = "https://accounts.zoho.com/oauth/v2/token"  # Default URL
        if self.state == 'in':
            base_url = "https://accounts.zoho.in/oauth/v2/token"
        elif self.state == 'com':
            base_url = "https://accounts.zoho.com/oauth/v2/token"
        elif self.state == 'eu':
            base_url = "https://accounts.zoho.eu/oauth/v2/token"
        elif self.state == 'jp':
            base_url = "https://accounts.zoho.jp/oauth/v2/token"
        elif self.state == 'com.au':
            base_url = "https://accounts.zoho.com.au/oauth/v2/token"

        url = f"{base_url}?refresh_token={self.refresh_token}&client_id={self.client_id}&client_secret={self.client_secrete}&grant_type=refresh_token"
        response = requests.post(url)

        if response.status_code == 200:
            decoded = json.loads(response.text)
            token = decoded.get('access_token')
            self.sudo().write({'zoho_token': token})
            data = {
                'var': token
            }
            if decoded.get('error'):
                raise ValidationError('Please Check Your Credentials To get ZOHO Token!')

            title = _("Generating New Access Token!")
            message = _("Action Success")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'sticky': False,
                }
            }

    def zoho_authtoken_generate_auto(self):
        check = self.env['zoho.books'].search([])
        if check.auto_sign is True:
            client = check.client_id
            refresh = check.refresh_token
            secrte = check.client_secrete
            base_url = "https://accounts.zoho.com/oauth/v2/token"  # Default URL
            if check.state == 'in':
                base_url = "https://accounts.zoho.in/oauth/v2/token"
            elif check.state == 'com':
                base_url = "https://accounts.zoho.com/oauth/v2/token"
            elif check.state == 'eu':
                base_url = "https://accounts.zoho.eu/oauth/v2/token"
            elif check.state == 'jp':
                base_url = "https://accounts.zoho.jp/oauth/v2/token"
            elif check.state == 'com.au':
                base_url = "https://accounts.zoho.com.au/oauth/v2/token"
            url = f"{base_url}?refresh_token={refresh}&client_id={client}&client_secret={secrte}&grant_type=refresh_token"
            response = requests.post(url)
            decoded = json.loads(response.text)
            token = decoded.get('access_token')
            check.write({'zoho_token': token})
            if decoded.get('error'):
                raise ValidationError(
                    'Please Check Your Credentials To get ZOHO Token !')

    # updated import_items_zoho code>::::::::::::::::::::::::::::::

    def import_items_zoho(self):
        if len(self) == 0:
            self = self.env['zoho.books'].search([])[0]
        self.zoho_authtoken_generate()

        rev = self.zoho_token
        headers = {
            "Authorization": "Zoho-oauthtoken " + rev,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        page = 1
        items = []
        zoho_item_ids = []

        while True:
            url = f"https://www.zohoapis.in/books/v3/items?organization_id={self.organization_id}&page={page}"
            response = requests.get(url, headers=headers)
            decoded = json.loads(response.text)
            items_data = decoded.get('items')
            items.extend(items_data)
            zoho_item_ids.extend(item["item_id"] for item in items_data if item.get("purchase_account_id"))
            page += 1
            if not items_data:
                break

        length = len(zoho_item_ids)
        check = self.env['product.template'].search([('zoho_id', 'in', zoho_item_ids)])
        removed_ids = []
        for rec in check:
            removed_ids.append(rec.zoho_id)
            zoho_item_ids.remove(rec.zoho_id)

        if not zoho_item_ids:
            return ('No IDs to import from Zoho.')

        for item_id in zoho_item_ids:
            headers = {"Authorization": "Zoho-oauthtoken " + rev, "Content-Type": "application/x-www-form-urlencoded"}
            url = f"https://www.zohoapis.in/books/v3/items/{item_id}?organization_id={self.organization_id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                decoded = json.loads(response.text)
                item_api = decoded.get('item')
                zoho_item_name = item_api.get('name')
                zoho_item_sku = item_api.get('sku')
                zoho_item_id = item_api.get('item_id')
                check_items_present = self.env['product.template'].search([('zoho_id', '=', False)], limit=1)

                if check_items_present:
                    contains_odoo = False
                    for rec in self.env['product.template'].search([]):
                        odoo_item_name = str(rec.name)
                        odoo_item_default_code = str(rec.default_code)
                        odoo_zoho_id = rec.zoho_id
                        if (zoho_item_name == odoo_item_default_code):
                            # (zoho_item_id == odoo_zoho_id) or
                            contains_odoo = True
                            name_ = rec
                            break

                    if contains_odoo:
                        if name_.type == 'product':
                            vals = {}
                            vals['default_code'] = zoho_item_name
                            vals['zoho_id'] = item_id
                            vals['is_zoho'] = True
                            if item_api.get('rate'):
                                vals['list_price'] = item_api.get('rate')
                                vals['description_sale'] = item_api.get('description')
                            if item_api.get('purchase_rate'):
                                vals['standard_price'] = item_api.get('purchase_rate')
                                vals['description_purchase'] = item_api.get('purchase_description')
                            if item_api.get('status') == 'active':
                                vals['active'] = True
                            if item_api.get('status') == 'inactive':
                                vals['active'] = False
                            name_.write(vals)

                        else:
                            raise ValidationError(
                                'Cannot change the type of an existing product!')
                    else:
                        contains_default_code = False
                        for rec in self.env['product.template'].search([]):
                            odoo_item_default_code = str(rec.default_code)
                            remove_first_zero = odoo_item_default_code[1:]
                            odoo_zoho_id = rec.zoho_id
                            if (zoho_item_name == remove_first_zero):
                                contains_default_code = True
                                name_ = rec
                                break
                        if contains_default_code:
                            if name_.type == 'product':
                                vals = {}
                                vals['default_code'] = zoho_item_name
                                # vals['drawing_number'] = name_.drawing_number
                                vals['zoho_id'] = item_id
                                vals['is_zoho'] = True
                                if item_api.get('rate'):
                                    vals['list_price'] = item_api.get('rate')
                                    vals['description_sale'] = item_api.get('description')
                                if item_api.get('purchase_rate'):
                                    vals['standard_price'] = item_api.get('purchase_rate')
                                    vals['description_purchase'] = item_api.get('purchase_description')
                                if item_api.get('status') == 'active':
                                    vals['active'] = True
                                if item_api.get('status') == 'inactive':
                                    vals['active'] = False
                                name_.write(vals)

                            else:
                                raise ValidationError(
                                    'Cannot change the type of an existing product!')
                        else:
                            continue

        # title = _("Generating New Access Token!")
        # message = _("Action Success")
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def refresh_page(self):
        pass

    def import_contacts_zoho(self):
        if len(self) == 0:
            self = self.env['zoho.books'].search([])[0]
        print("haakjflkasfksjaflkasjf;lkaj")
        self.zoho_authtoken_generate()
        purchases = []
        zoho_purchases_id = []

        page = 1
        while True:
            url = f"https://www.zohoapis.in/books/v3/contacts?organization_id={self.organization_id}&page={page}"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.zoho_token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            response = requests.get(url, headers=headers)
            print("ressssssssssppppppppppnnnnnnnnse", response)
            if response.status_code != 200:
                break
            result = response.json().get("contacts")
            print("resssssssssssssullllllllllllltttttttt", result)
            purchases.extend(result)
            zoho_purchases_id.extend(
                [purchase["contact_id"] for purchase in result if purchase['contact_type'] in 'vendor'])
            if len(result) < 10:
                break
            page += 1

        purchase_ids = zoho_purchases_id
        ####### 1. Method To Pass Only New Id's and removing ALready exist Id's
        check = self.env['res.partner'].search([('zoho_id', '=', purchase_ids)])
        removed_ids = []
        for rec in check:
            removed_ids.append(rec.zoho_id)
            purchase_ids.remove(rec.zoho_id)

        ####### 2. Another Method To Pass Only New Id's and removing ALready exist Id's
        # check = self.env['res.partner'].search([('zoho_id', 'in', purchase_ids)])
        # removed_ids = [rec.zoho_id for rec in check]
        # purchase_ids = [new_id for new_id in purchase_ids if new_id not in removed_ids]
        # print("Already Exist Id", removed_ids)
        # print("After removed Already Exist", purchase_ids)
        if not purchase_ids:
            return "No purchase IDs available."
        while purchase_ids:
            url2 = f"https://www.zohoapis.in/books/v3/contacts/{purchase_ids.pop()}?organization_id={self.organization_id}"
            headers = {
                "Authorization": "Zoho-oauthtoken " + self.zoho_token,
                "Content-Type": "application/json"
            }
            try:
                response = requests.get(url2, headers=headers)
                response.raise_for_status()
                # if response.status_code == 200:
                decoded = json.loads(response.text)
                contact_api = decoded.get('contact')
                contact_id = contact_api.get('contact_id')
                zoho_contact_name = contact_api.get('contact_name')
                check_items_present = self.env['res.partner'].search([('zoho_id', '=', False)], limit=1)
                if check_items_present:
                    zoho_contact_name_clean = re.sub('[^A-Za-z0-9]+', '', zoho_contact_name)
                    change_zoho_upper = zoho_contact_name_clean.upper()
                    found_in_odoo = False
                    for rec in self.env['res.partner'].search([]):
                        odoo_contact_name = rec.name
                        odoo_contact_name_clean = re.sub('[^A-Za-z0-9]+', '', odoo_contact_name)
                        change_upper = odoo_contact_name_clean.upper()
                        if change_zoho_upper in change_upper:
                            found_in_odoo = True
                            name_ = rec
                            break

                    if found_in_odoo:
                        vals = {
                            'name': zoho_contact_name,
                            'contact_type': contact_api.get('contact_type'),
                            'zoho_id': contact_id,
                            'is_zoho': True,
                            'website': contact_api.get('website'),
                            'email': contact_api.get('email'),
                            'phone': contact_api.get('phone'),
                            'mobile': contact_api.get('mobile'),
                        }
                        billing_address = contact_api['billing_address']
                        address = billing_address['address']
                        street2 = billing_address['street2']
                        city = billing_address['city']
                        state = billing_address['state']
                        country = billing_address['country']
                        zip = billing_address['zip']
                        vals['street'] = address
                        vals['street2'] = street2
                        vals['city'] = city
                        country_id = self.env['res.country'].search([('name', '=', country)], limit=1)
                        if country_id:
                            vals['country_id'] = country_id.id
                        state_id = self.env['res.country.state'].search(
                            [('name', '=', state), ('country_id', '=', country_id.id)], limit=1)
                        if state_id:
                            vals['state_id'] = state_id.id
                        vals['zip'] = zip
                        name_.write(vals)


                    else:
                        vals = {
                            'name': zoho_contact_name,
                            'contact_type': contact_api.get('contact_type'),
                            'zoho_id': contact_id,
                            'is_zoho': True,
                            'website': contact_api.get('website'),
                            'email': contact_api.get('email'),
                            'phone': contact_api.get('phone'),
                            'mobile': contact_api.get('mobile'),
                        }
                        billing_address = contact_api['billing_address']
                        address = billing_address['address']
                        street2 = billing_address['street2']
                        city = billing_address['city']
                        state = billing_address['state']
                        country = billing_address['country']
                        zip = billing_address['zip']
                        vals['street'] = address
                        vals['street2'] = street2
                        vals['city'] = city
                        country_id = self.env['res.country'].search([('name', '=', country)], limit=1)
                        if country_id:
                            vals['country_id'] = country_id.id
                        state_id = self.env['res.country.state'].search(
                            [('name', '=', state), ('country_id', '=', country_id.id)], limit=1)
                        if state_id:
                            vals['state_id'] = state_id.id
                        vals['zip'] = zip
                        create_contact = self.env['res.partner'].create(vals)
                        if create_contact:
                            print("Zoho contact name is not present in Odoo contact name.")
                # time.sleep(1.5)
            except requests.exceptions.RequestException as err:
                print("Error occurred during API call:", err)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def get_list_of_zoho_ids_of_po_in_odoo(self):
        list_of_zoho_ids = []
        purchaseorder = self.env['purchase.order'].search([('zoho_id', '!=', False)])
        for po in purchaseorder:
            list_of_zoho_ids.append(po.zoho_id)
        return list_of_zoho_ids

    def get_filtered_zoho_ids(self):
        print("get finlertere zoho ids")
        import http.client
        conn = http.client.HTTPSConnection("www.zohoapis.in")
        headers = {
            'Authorization': f"Zoho-oauthtoken {self.zoho_token}"}

        has_more_page = True
        page = 1
        filtered_zoho_ids_list = []
        unwanted_po_num = []
        unwanted_po = self.env['unwanted.po'].search([])
        for po in unwanted_po:
            unwanted_po_num.append(po.po_num)
        while has_more_page:
            print("under the while has more page")
            conn.request("GET",
                         f"/books/v3/purchaseorders?organization_id={self.organization_id}&page={page}",
                         headers=headers)

            res = conn.getresponse()
            data = res.read()

            # print(data.decode("utf-8"))
            response_string = data.decode("utf-8")
            response = json.loads(response_string)
            purchase_orders_list_per_page = response['purchaseorders']
            existing_po_ids = self.get_list_of_zoho_ids_of_po_in_odoo()
            for po in purchase_orders_list_per_page:
                if (po['status'] != 'draft' and po['purchaseorder_number'] not in unwanted_po_num and
                        po['purchaseorder_id'] not in existing_po_ids):
                    filtered_zoho_ids_list.append(po['purchaseorder_id'])
            has_more_page = response['page_context']['has_more_page']
            print("???????????????????????", has_more_page)
            page += 1
        return filtered_zoho_ids_list

    def check_line_items_in_odoo(self, line_items):
        item_zoho_ids = []
        products = self.env['product.template'].search([('zoho_id', '!=', False), ('default_code', '!=', False)])
        for prod in products:
            item_zoho_ids.append(prod.zoho_id)
        for item in line_items:
            if item['item_id'] not in item_zoho_ids:
                return False
        return True

    def get_list_of_purchase_orders_to_be_created(self, ids_to_be_imported):
        print("ids_to_be_imported", ids_to_be_imported)
        list_of_pos_to_be_created = []
        waste_po_list = []
        import http.client
        conn = http.client.HTTPSConnection("www.zohoapis.in")
        headers = {
            'Authorization': f"Zoho-oauthtoken {self.zoho_token}"}
        for idx, zoho_id in enumerate(ids_to_be_imported):
            print(idx, "zoho_id", zoho_id)
            index = ids_to_be_imported.index(zoho_id)
            if index != 0 and (index % 50) == 0:
                import time
                # time.sleep(60)
            conn.request("GET", f"/books/v3/purchaseorders/{zoho_id}?organization_id={self.organization_id}",
                         headers=headers)

            res = conn.getresponse()
            print(".....................res", res)
            data = res.read()
            print("............", data)
            response = json.loads(data.decode('utf-8'))
            print("responseeeeeeeeeeeeeeeeee", response)
            is_line_item_in_odoo = self.check_line_items_in_odoo(response['purchaseorder']["line_items"])
            if is_line_item_in_odoo:
                list_of_pos_to_be_created.append(response['purchaseorder'])
            else:
                self.env['unwanted.po'].create({'po_num': response['purchaseorder']['purchaseorder_number'],
                                                'zoho_id': response['purchaseorder']['purchaseorder_id']})
                waste_po_list.append(response['purchaseorder']['purchaseorder_number'])

        return [list_of_pos_to_be_created, waste_po_list]

    def prepare_order_line_values(self, line_items):
        order_line_items = []
        for item in line_items:
            product = self.env['product.template'].search([('zoho_id', '=', item['item_id'])])
            # is_same = check_same_units(zoho_unit=item['unit'], odoo_unit=product.uom_po_id.name)
            #
            # if is_same is False:
            #     product_qty = 0
            # else:
            #     product_qty = item['quantity']
            vals = {'product_id': product.id,
                    'name': item['description'],
                    'ordered_qty': str(item['quantity']) + item['unit'],
                    # 'uom_line_value': product_uom_value,
                    'product_qty': item['quantity'],
                    'product_uom': product.uom_po_id.id,
                    'price_unit': (item['rate']),
                    'price_subtotal': item['item_total'],
                    'zoho_total_price': item['item_total']
                    # 'std_quantity': item['quantity'],
                    # 'std_unit_price': item['rate']
                    }
            order_line_items.append((0, 0, vals))
        return order_line_items

    def prepare_values(self, po):
        po_date = po['date']
        approve_date = datetime.strptime(po_date, '%Y-%m-%d')
        po_expected_date = po['delivery_date']
        if po_expected_date:

            planned_date = datetime.strptime(po_expected_date, '%Y-%m-%d')
        else:
            planned_date = False
        vendor = self.env['res.partner'].search([('zoho_id', '=', po['vendor_id'])])
        vals = {'name': po['purchaseorder_number'],
                'partner_id': vendor.id,
                'zoho_id': po['purchaseorder_id'],
                'is_zoho': True,
                'l10n_in_gst_treatment': vendor.l10n_in_gst_treatment,
                'date_approve': approve_date,
                'date_planned': planned_date,
                'order_line': self.prepare_order_line_values(po['line_items'])}
        return vals

    def create_po(self, list_of_pos_to_be_created):
        created_pos = []
        for po in list_of_pos_to_be_created:
            vals = self.prepare_values(po)
            created_po = self.env['purchase.order'].create(vals)
            created_pos.append(created_po)
            created_po.button_confirm()
            new_transfer = self.env['stock.picking'].search([('origin', '=', created_po.name)])
            # for line in new_transfer.move_ids_without_package:
            #     line.uom_line_value = line.product_id.uom_value if line.product_id.uom_value != 0 else 1
        return created_pos

    def create_log_history(self, count, state, list_pos, po_num):
        current_date_time = datetime.today()
        po_ids = []
        for po in list_pos:
            po_ids.append(po.id)
        self.env['log.history'].create({'date': current_date_time,
                                        'count': count,
                                        'state': state,
                                        'purchase_order_ids': po_ids,
                                        'po_number': po_num})

    def import_purchase_zoho(self):
        print("import purchase zoho,,,,,,,,,,,,,,,,")
        if len(self) == 0:
            self = self.env['zoho.books'].search([])[0]
        self.zoho_authtoken_generate()
        filtered_zoho_id_list = self.get_filtered_zoho_ids()
        list_of_pos_to_be_created = self.get_list_of_purchase_orders_to_be_created(filtered_zoho_id_list)
        created_pos = self.create_po(list_of_pos_to_be_created[0])
        self.create_log_history(count=len(list_of_pos_to_be_created[0]),
                                state="Imported Successfully",
                                list_pos=created_pos,
                                po_num=False)
        if len(list_of_pos_to_be_created[1]) > 0:
            self.create_log_history(count=len(list_of_pos_to_be_created[0]),
                                    state="Not Imported PO's",
                                    list_pos=[],
                                    po_num=list_of_pos_to_be_created[1])
        return {
            'count': len(list_of_pos_to_be_created[0]),
            'length': len(list_of_pos_to_be_created[1]),
        }

    # *******************************************************************************************************************
    # *******************************************************************************************************************
    def action_success(self):
        title = _("Generating New Access Token!")
        message = _("Action Success")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': False,
            }
        }

    def action_warning(self):
        title = _("Generating New Access Token!")
        message = _("Action Success")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'type': 'warning',
                'message': message,
                'sticky': False,
            }
        }

    log_history_ids = fields.One2many("log.history", "zoho_book_id", string="Zoho")


class LogHistory(models.Model):
    _name = 'log.history'

    date = fields.Datetime(string="Datetime")
    count = fields.Integer(string="count")
    visible = fields.Char()
    state = fields.Text(string="Status")
    zoho_book_id = fields.Many2one('zoho.books')
    purchase_order_ids = fields.Many2many('purchase.order', string="Purchase Orders")
    po_number = fields.Html(string="Rejected PO's")


class ResCompany(models.Model):
    _inherit = 'res.company'

    zoho_ids = fields.Many2many('zoho.books', string="zoho cred")
    # char = fields.Char('NOTES')


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    decimal_places = fields.Integer(readonly=False)



