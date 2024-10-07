from _pydecimal import Decimal

from odoo import models, api, fields, _
import xlwt
import base64
from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import date
from pytz import timezone
from operator import itemgetter
import time


class InventoryReportWizard(models.TransientModel):
    _name = 'inventory_report'

    def get_percent(self, total, qty, po_num=None):
        print("total>>>>>>>.", total)
        print("qty>>>>>>>>>.", qty)
        if total is None:
            total = 0
        if qty is None:
            qty = 0
        if total < qty:
            po = self.env['purchase.order'].search([('id', '=', po_num)])
            raise ValidationError(f"You have manually changed the inward quantity in PO: {po.name} after quality check,"
                                  f" Please correct that.")
        if qty:
            percent = (qty / total) * 100
            return round(percent, 2)
        else:
            return 0

    def default_get(self, fields_list):
        res = super(InventoryReportWizard, self).default_get(fields_list)
        company = self.env.company
        res['company_id'] = company.id
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        res['date_from'] = formatted_date
        res['date_to'] = formatted_date
        return res

    hi = fields.Char('HI')
    company_id = fields.Many2one('res.company', "Company", readonly=True)
    date_from = fields.Date("FROM", required=True)
    date_to = fields.Date("TO", required=True)
    categ_id = fields.Many2many('product.category', string='Product Category')
    vendors = fields.Many2many('res.partner')
    products = fields.Many2many('product.template', copy=False)
    product = fields.Many2one('product.template', domain="[('categ_id', 'in', categ_id)]")
    warehouse = fields.Many2one('stock.warehouse')
    location = fields.Many2one('stock.location')
    report_type = fields.Selection([('movement_report', 'MOVEMENT REPORT'),
                                    ('view_movement', 'INVENTORY REPORT'),
                                    ('vendor_report', 'VENDOR RATE'),
                                    ('product_rate_report', 'PRODUCTS RATE')], string='Report Type',
                                   default='view_movement')

    default_code = fields.Char()
    name = fields.Char()
    quantity = fields.Float()
    uom = fields.Char()
    value = fields.Float()
    category = fields.Char()
    qty_on_fromdate = fields.Float('OPENING QUANTITY')
    qty_in = fields.Float('IN')
    qty_out = fields.Float('OUT')
    qty_on_todate = fields.Float('CLOSING QUANTITY')
    val_on_fromdate = fields.Float('OPENING VALUE')
    val_in = fields.Float('VALUE IN')
    val_out = fields.Float('VALUE OUT')
    val_on_todate = fields.Float('CLOSING VALUE')
    type_of_report = fields.Selection([('pdf', 'PDF'),
                                       ('xl', 'EXCEL')], default='xl', required=True)
    summary_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Movement Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')

    @api.onchange('report_type')
    def onchange_of_report_type(self):
        self.products = False
        self.categ_id = False

    @api.onchange('vendors')
    def onchange_of_vendors(self):
        return {
            'domain': {
                'vendors': [('contact_type', '=', 'vendor')]
            }
        }

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        print('under onchange!!!!!!!!!!!')
        print('categIIIIIIDDDDDDDDDD', self.categ_id)
        if self.categ_id:
            product_ids_list = []
            for rec in self.categ_id:
                print('selfcateg', rec.name)
                products = self.env['product.template'].search([('categ_id.name', '=', rec.name)])
                print('products', products.ids)
                for id_list in products:
                    print('under if')
                    product_ids_list.append(id_list.id)
            self.products = product_ids_list
        else:
            print('under else')
            self.products = False

    """*****************************************************************************************************************
    ***********************************************INVENTORY REPORT BEGIN***********************************************
    ****************************************************************************************************************"""

    def get_ob_cb(self, arg_date_from, arg_date_to):
        print('self.read(of zero', self.read())
        date_from = arg_date_from.strftime("%Y-%m-%d, 00:01:10")
        date_to = arg_date_to.strftime("%Y-%m-%d, 23:59:10")
        date_from = datetime.strptime(date_from, "%Y-%m-%d, %H:%M:%S")
        date_to = datetime.strptime(date_to, "%Y-%m-%d, %H:%M:%S")
        print(date_from)
        print(date_to)
        stock_move = self.env['stock.move.line'].search([('product_id.default_code', '=', self.product.default_code)])

        qty_list_until_from_date = []
        qty_list_after_fromdate_to_todate = []
        for move in stock_move:
            if move.date <= date_from:
                if move.location_id.id == 8:
                    qty_list_until_from_date.append(-move.quantity_product_uom)
                else:
                    qty_list_until_from_date.append(move.quantity_product_uom)
            elif (move.date > date_from) and (move.date <= date_to):
                if move.location_id.id == 8:
                    qty_list_after_fromdate_to_todate.append(-move.quantity_product_uom)
                else:
                    qty_list_after_fromdate_to_todate.append(move.quantity_product_uom)
        opening_qty_on_fromdate = 0.0
        for qty in qty_list_until_from_date:
            opening_qty_on_fromdate = opening_qty_on_fromdate + qty
        sum_of_qty_from_fromdate_to_todate = 0.0
        for qty in qty_list_after_fromdate_to_todate:
            sum_of_qty_from_fromdate_to_todate = sum_of_qty_from_fromdate_to_todate + qty
        closing_qty_on_todate = opening_qty_on_fromdate + sum_of_qty_from_fromdate_to_todate
        ob_cb = {
            'opening_balance': opening_qty_on_fromdate,
            'closing_balance': closing_qty_on_todate,
        }
        return ob_cb

    def get_in_out_recs(self, product_id, date_from, date_to):
        incoming_record_list = []
        outgoing_record_list = []
        stock_move_records = self.env['stock.move.line'].search([
            ('product_id.id', '=', product_id), ('state', '=', 'done'),
            ('date', '>=', date_from), ('date', '<=', date_to)])
        print('stock_move_records', stock_move_records)
        print('length of stock_move_records', len(list(stock_move_records)), ">>>>>>>", stock_move_records)

        for rec in stock_move_records:
            utc_date = rec.date
            india_date = utc_date.astimezone(timezone('Asia/Kolkata'))
            if rec.location_id.id == 8:
                if rec.move_id.partner_id:
                    partner_name = rec.move_id.partner_id.name if rec.move_id.partner_id.name else 'Admin'
                else:
                    partner_name = rec.create_uid.name
                rec_data = {
                    'date': india_date.strftime("%d-%m-%Y  %H:%M:%S"),
                    'voucher_number': rec.reference,
                    'partner_name': partner_name,
                    'qty': rec.quantity_product_uom
                }
                outgoing_record_list.append(rec_data)
            else:
                if rec.move_id.partner_id:
                    partner_name = rec.move_id.partner_id.name if rec.move_id.partner_id.name else 'Admin'
                else:
                    partner_name = rec.create_uid.name

                rec_data = {
                    'date': india_date.strftime("%d-%m-%Y  %H:%M:%S"),
                    'voucher_number': rec.reference,
                    'partner_name': partner_name,
                    'qty': rec.quantity_product_uom
                }
                incoming_record_list.append(rec_data)
        in_out_recs = {
            'incoming_records': incoming_record_list,
            'outgoing_records': outgoing_record_list
        }

        return in_out_recs

    def xlwt_movement_report(self):
        ob_cb = self.get_ob_cb(self.date_from, self.date_to)
        in_out_recs = self.get_in_out_recs(self.product.id, self.date_from, self.date_to)
        print("..............................................", in_out_recs)
        if len(in_out_recs['incoming_records']) == 0 and len(in_out_recs['outgoing_records']) == 0:
            raise ValidationError("No movements within the selected date")
        file_name = 'Report.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        format0 = xlwt.easyxf(
            'font:height 500,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        formathead1 = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour white;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;alignment: wrap True')
        formathead2 = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour green;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;alignment: wrap True')
        formathead3 = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour red;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;alignment: wrap True')
        format1 = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz left; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        format2 = xlwt.easyxf('font:bold True;align: horiz left')
        format3 = xlwt.easyxf('align: horiz left; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        style = xlwt.XFStyle()
        sheet = workbook.add_sheet("Movement Report")
        sheet.col(0).width = int(7 * 260)
        sheet.col(1).width = int(30 * 260)
        sheet.col(2).width = int(40 * 260)
        sheet.col(3).width = int(20 * 260)
        sheet.col(6).width = int(7 * 260)
        sheet.col(7).width = int(30 * 260)
        sheet.col(8).width = int(40 * 260)
        sheet.col(9).width = int(40 * 260)
        sheet.row(0).height_mismatch = True
        sheet.row(0).height = 150 * 4
        sheet.row(1).height_mismatch = True
        sheet.row(1).height = 150 * 2
        sheet.row(2).height_mismatch = True
        sheet.row(2).height = 150 * 3
        sheet.write_merge(0, 0, 0, 13, 'Movement Report', format0)
        sheet.write_merge(1, 4, 0, 13,
                          f"Product-Ref: {self.product.default_code}    From Date: {self.date_from}    To Date: {self.date_to}\n "
                          f"Product-Name: {self.product.name}    Opening Balance: {ob_cb['opening_balance']}    Closing Balance: {ob_cb['closing_balance']}\n "
                          f"Report Date: {date.today()}", formathead1)
        sheet.write_merge(6, 9, 0, 4, f"INWARD \n{self.product.name}", formathead2)
        sheet.write(10, 0, 'Sl.No#', format1)
        sheet.write(10, 1, 'Date', format1)
        sheet.write(10, 2, 'Reference Number', format1)
        sheet.write(10, 3, 'Partner Name', format1)
        sheet.write(10, 4, 'Quantity', format1)
        row = 11
        s_no = 0
        for rec in in_out_recs['incoming_records']:
            s_no += 1
            sheet.write(row, 0, s_no, format3)
            sheet.write(row, 1, str(rec['date']), format3)
            sheet.write(row, 2, rec['voucher_number'], format3)
            sheet.write(row, 3, rec['partner_name'], format3)
            sheet.write(row, 4, rec['qty'], format3)
            row += 1

        sheet.write_merge(6, 9, 6, 10, f"OUTWARD \n{self.product.name}", formathead3)
        sheet.write(10, 6, 'Sl.No#', format1)
        sheet.write(10, 7, 'Date', format1)
        sheet.write(10, 8, 'Reference Number', format1)
        sheet.write(10, 9, 'Partner Name', format1)
        sheet.write(10, 10, 'Quantity', format1)
        row = 11
        s_no = 0
        for rec in in_out_recs['outgoing_records']:
            s_no += 1
            sheet.write(row, 6, s_no, format3)
            sheet.write(row, 7, str(rec['date']), format3)
            sheet.write(row, 8, rec['voucher_number'], format3)
            sheet.write(row, 9, rec['partner_name'], format3)
            sheet.write(row, 10, rec['qty'], format3)
            row += 1
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)

        file_content = base64.b64encode(fp.getvalue())
        self.write({
            'file_name': file_content,

        })
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=inventory_report&id=%s&field=file_name&download=true&filename=movement_report.xls' % (
                self.id),
            'target': 'self'
        }

    def products_inventory_details(self, from_date, to_date, i_products, called_from_barcode=False):
        if to_date < from_date:
            raise ValidationError(_("The \"Date To\"  must be the SAME OR AFTER the \"Date From\"."))
        date_from = from_date.strftime("%Y-%m-%d, 00:01:10")
        date_to = to_date.strftime("%Y-%m-%d, 23:59:10")
        date_from = datetime.strptime(date_from, "%Y-%m-%d, %H:%M:%S")
        date_to = datetime.strptime(date_to, "%Y-%m-%d, %H:%M:%S")
        print("date from", date_from)
        print("date_to", date_to)
        products = []
        print("................iproductsl...........", i_products)
        for record in i_products:
            if called_from_barcode:
                print("%%%%%%%%%%%%%%record.proudct id . anmename$$$$$$$44", record.product_id.name)
                valuation = self.env['stock.valuation.layer'].search([('product_id', '=', record.product_id.id)])
            else:
                valuation = self.env['stock.valuation.layer'].search([('product_id', '=', record.id)])
            qty_list_untill_fromdate = []
            qty_list_after_fromdate_to_todate = []
            if len(valuation) != 0:
                for rec in valuation:
                    print("reccccccccccuh", rec)
                    if rec.create_date <= date_from:
                        qty_list_untill_fromdate.append(rec.quantity)
                    elif (rec.create_date > date_from) and (rec.create_date <= date_to):
                        qty_list_after_fromdate_to_todate.append(rec.quantity)
            else:
                qty_list_untill_fromdate.append(0)
                qty_list_after_fromdate_to_todate.append(0)
            print("qty list until from date", qty_list_untill_fromdate)
            print("qty between from and to", qty_list_after_fromdate_to_todate)
            quantity_on_from_date = sum(qty_list_untill_fromdate)
            quantity_on_to_date = sum(qty_list_after_fromdate_to_todate) + quantity_on_from_date
            print('quantity_on from date', quantity_on_from_date)
            print("quantity_on_to_date", quantity_on_to_date)
            print("after from date to to_date.....", qty_list_after_fromdate_to_todate)

            plus_quants = []
            minus_quants = []
            for quant in qty_list_after_fromdate_to_todate:
                if quant < 0:
                    minus_quants.append(quant)
                else:
                    plus_quants.append(quant)
            in_qtys = sum(plus_quants)
            out_qtys = sum(minus_quants)

            print("in_qtys>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", plus_quants)
            print("out_qtys>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", minus_quants)
            # *****************************************************************
            if called_from_barcode:
                product_details = {
                    'date_from': date_from,
                    'date_to': date_to,
                    'default_code': record.product_id.default_code if record.product_id.default_code else '0',
                    'name': record.product_id.name,
                    'qty_on_todate': round(quantity_on_to_date, 2),
                }
            else:
                product_details = {
                    'date_from': date_from,
                    'date_to': date_to,
                    'default_code': record.default_code if record.default_code else '0',
                    'name': record.name,
                    'quantity': round(record.qty_available, 2),
                    'uom': record.uom_id.name,
                    'value': record.standard_price,
                    'category': record.categ_id.name,
                    'qty_on_fromdate': round(quantity_on_from_date, 2),
                    'qty_in': in_qtys,
                    'qty_out': out_qtys,
                    'qty_on_todate': round(quantity_on_to_date, 2),
                    'val_on_fromdate': round(quantity_on_from_date * record.standard_price, 2),
                    'val_in': in_qtys * record.standard_price,
                    'val_out': out_qtys * record.standard_price,
                    'val_on_todate': round(quantity_on_to_date * record.standard_price, 2),
                }
            products.append(product_details)
        return products

    def view_movement(self):

        products = self.products_inventory_details(self.date_from, self.date_to, self.products)
        date_from = products[0]['date_from'].strftime("%d-%m-%Y")
        date_to = products[0]['date_to'].strftime("%d-%m-%Y")
        user = "Administrator"
        today_date = datetime.now()
        current_date = today_date.strftime('%d/%m/%Y')

        workbook = xlwt.Workbook(encoding="UTF-8")
        sheet = workbook.add_sheet("Inventory Report")

        sheet.row(0).height_mismatch = True
        sheet.row(0).height = 150 * 4

        sheet.row(2).height_mismatch = True
        sheet.row(2).height = 150 * 3

        sheet.row(4).height_mismatch = True
        sheet.row(4).height = 150 * 3

        sheet.col(0).width = int(10 * 260)
        sheet.col(1).width = int(20 * 260)
        sheet.col(2).width = int(60 * 260)
        sheet.col(3).width = int(20 * 260)
        sheet.col(4).width = int(20 * 260)
        sheet.col(5).width = int(40 * 260)
        sheet.col(6).width = int(20 * 260)
        sheet.col(7).width = int(20 * 260)
        sheet.col(8).width = int(40 * 260)
        sheet.col(9).width = int(20 * 260)
        sheet.col(10).width = int(20 * 260)
        sheet.col(11).width = int(20 * 260)
        sheet.col(12).width = int(20 * 260)
        sheet.col(13).width = int(20 * 260)
        sheet.col(14).width = int(20 * 260)

        lavender_bold_centre = xlwt.easyxf(
            'font:height 500,bold True;pattern: pattern solid, fore_colour teal;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')

        violet_bold_left = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour violet;align: horiz left; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;alignment: wrap True')
        violet_bold_center = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour violet;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;alignment: wrap True')
        violet_bold_right = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour violet;align: horiz right; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;alignment: wrap True')
        indigo_bold_left = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour indigo;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;alignment: wrap True')

        empty_bold_right = xlwt.easyxf('align: horiz right;font:height 500,bold True;pattern: pattern solid;')
        bold_center = xlwt.easyxf('font:bold True;align: horiz center')
        bold_right = xlwt.easyxf('font:bold True;align: horiz right')
        bold_left = xlwt.easyxf('font:bold True;align: horiz left')

        sheet.write_merge(0, 0, 0, 13, 'Inventory Valuation Report', lavender_bold_centre)
        sheet.write_merge(2, 2, 0, 13,
                          f"Date From: {date_from}      Date To:{date_to}      Login User:{user}    printed ON:{current_date}",
                          violet_bold_center)
        headers = ['S.NO', 'PART NUMBER', 'DESCRIPTION', 'QTY', 'UOM', 'OPENING QUANTITY', 'QUANTITY IN',
                   'QUANTITY OUT', 'CURRENT QUANTITY', 'VALUE', 'OPENING VALUE', 'VALUE IN', 'VALUE OUT',
                   'CLOSING VALUE']
        for col, header in enumerate(headers):
            sheet.write(4, col, header, indigo_bold_left)
        row = 5
        sorted_products = sorted(products, key=itemgetter('default_code'))
        for idx, product in enumerate(sorted_products):
            sheet.write(row, 0, idx + 1, bold_center)
            sheet.write(row, 1, product.get('default_code') or 'nil', bold_center)
            sheet.write(row, 2, product.get('name') or 'nil', bold_left)
            sheet.write(row, 3, product.get('quantity') or '0', bold_right)
            sheet.write(row, 4, product.get('uom') or 'nil', bold_center)
            sheet.write(row, 5, product.get('qty_on_fromdate') or '0', bold_right)
            sheet.write(row, 6, product.get('qty_in') or '0', bold_right)
            sheet.write(row, 7, product.get('qty_out') or '0', bold_right)
            sheet.write(row, 8, product.get('quantity') or '0', bold_right)
            sheet.write(row, 9, product.get('value') or '0', bold_right)
            sheet.write(row, 10, product.get('val_on_fromdate') or '0', bold_right)
            sheet.write(row, 11, product.get('val_in') or '0', bold_right)
            sheet.write(row, 12, product.get('val_out') or '0', bold_right)
            sheet.write(row, 13, product.get('val_on_todate') or '0', bold_right)

            row += 1
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)

        file_content = base64.b64encode(fp.getvalue())
        self.write({
            'file_name': file_content,

        })
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=inventory_report&id=%s&field=file_name&download=true&filename=inventory_report.xls' % (
                self.id),
            'target': 'self'
        }

    def create_multiple_records(self, vals_list):
        print("inventory report", self.env['inventory_report'].search([]))
        inventory_report = self.env['inventory_report'].search([])
        inv_report_id_list = []
        for rec in inventory_report:
            inv_report_id_list.append(rec.id)
        n = len(inv_report_id_list)
        print("length of the list", n)
        active_id = inv_report_id_list[n - 1]
        # active_id = self.env.context.get('active_id')
        self.env['inventory_report'].search([('id', '!=', active_id)]).unlink()
        created_records = self.env['inventory_report']
        for vals in vals_list:
            record = self.env['inventory_report'].create(vals)
            created_records += record

    def get_vendor_detail_dict_list(self):
        vendor_ids_list = [vendor.id for vendor in self.vendors]
        if len(self.vendors) == 0:
            result = self.env['quality.apex'].search(
                [('write_date', '>=', self.date_from), ('write_date', '<=', self.date_to), ('state', '=', 'done')])
        else:
            result = self.env['quality.apex'].search(
                [('vendor_id', 'in', vendor_ids_list), ('write_date', '>=', self.date_from),
                 ('write_date', '<=', self.date_to), ('state', '=', 'done')])
            if len(result) == 0:
                raise ValidationError("Selected vendor has no records in Quality.")

        vendors_list = []
        [vendors_list.append(qc.vendor_id) for qc in result if qc.vendor_id not in vendors_list]
        print("vendors list", vendors_list)
        vendor_detail_dict_list = []
        for vendor in vendors_list:
            product_grouped = self.env['quality.apex'].read_group(
                [('vendor_id', '=', vendor.id), ('write_date', '>=', self.date_from),
                 ('write_date', '<=', self.date_to), ('state', '=', 'done')],
                ['po_num:array_agg', 'quantity:array_agg', 'passed:array_agg', 'failed:array_agg'],
                ['product_id']
            )
            print("product_grouped", product_grouped)
            products_list = [rec['product_id'][0] for rec in product_grouped]
            po_num_list_list = [rec['po_num'] for rec in product_grouped]
            inward_list_list = [rec['quantity'] for rec in product_grouped]
            passed_list_list = [rec['passed'] for rec in product_grouped]
            failed_list_list = [rec['failed'] for rec in product_grouped]

            vendor_detail_dict_list.append({
                f"{vendor.name}": [{product: {"po_nums_list": po_num_list_list[index],
                                              "inward_list": inward_list_list[index],
                                              "passed_list": passed_list_list[index],
                                              "failed_list": failed_list_list[index]}} for index, product in
                                   enumerate(products_list)]
            })

        return vendor_detail_dict_list

    def get_product_detail_dict_list(self):
        product_ids_list = [product.id for product in self.products]
        if len(self.products) == 0:
            result = self.env['quality.apex'].search(
                [('write_date', '>=', self.date_from), ('write_date', '<=', self.date_to), ('state', '=', 'done')])
        else:
            result = self.env['quality.apex'].search(
                [('product_id', 'in', product_ids_list), ('write_date', '>=', self.date_from),
                 ('write_date', '<=', self.date_to), ('state', '=', 'done')])
            if len(result) == 0:
                raise ValidationError("Selected product has no records in Quality.")

        products_list = []
        [products_list.append(qc.product_id) for qc in result if qc.product_id not in products_list]
        print("vendors list", products_list)
        product_detail_dict_list = []

        for product in products_list:
            vendor_grouped = self.env['quality.apex'].read_group(
                [('product_id', '=', product.id), ('write_date', '>=', self.date_from),
                 ('write_date', '<=', self.date_to), ('state', '=', 'done')],
                ['po_num:array_agg', 'quantity:array_agg', 'passed:array_agg', 'failed:array_agg'],
                ['vendor_id']
            )
            print("product_grouped", vendor_grouped)
            vendors_list = [rec['vendor_id'][0] for rec in vendor_grouped]
            po_num_list_list = [rec['po_num'] for rec in vendor_grouped]
            inward_list_list = [rec['quantity'] for rec in vendor_grouped]
            passed_list_list = [rec['passed'] for rec in vendor_grouped]
            failed_list_list = [rec['failed'] for rec in vendor_grouped]

            product_detail_dict_list.append({
                f"{product.name}": [{vendor: {"po_nums_list": po_num_list_list[index],
                                              "inward_list": inward_list_list[index],
                                              "passed_list": passed_list_list[index],
                                              "failed_list": failed_list_list[index]}} for index, vendor in
                                    enumerate(vendors_list)]
            })

        return product_detail_dict_list

    def xlwt_vendor_report(self):
        today_date = datetime.now()
        current_date_str = today_date.strftime('%d/%m/%Y')
        from_date = self.date_from
        from_date_str = from_date.strftime('%d/%m/%Y')
        to_date = self.date_to
        to_date_str = to_date.strftime('%d/%m/%Y')
        if self.report_type == 'vendor_report':
            detail_dict_list = self.get_vendor_detail_dict_list()
            filename = f'vendor_report_{datetime.today()}'
            print("vendor_detail_dict_list", detail_dict_list)
        else:
            detail_dict_list = self.get_product_detail_dict_list()
            filename = f'product_report_{datetime.today()}'
            print("product_detail_dict_list", detail_dict_list)
        file_name = 'vendor_report.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        style.font.bold = 1

        style.pattern.pattern_fore_colour = 1
        lavender_bold_centre = xlwt.easyxf(
            'font:height 500,bold True;pattern: pattern solid, fore_colour teal;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        periwinkle_bold_left = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour periwinkle;align: horiz left; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;alignment: wrap True')
        periwinkle_bold_center = xlwt.easyxf(
            'font:height 200,bold True;pattern: pattern solid, fore_colour periwinkle;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        sea_green_bold_left = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour sea_green;align: horiz left; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        olive_ega_bold_center = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour olive_ega;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        red_bold_centre = xlwt.easyxf(
            'font:height 250,bold True, color white;pattern: pattern solid, fore_colour dark_red_ega;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        dark_green_bold_centre = xlwt.easyxf(
            'font:height 250,bold True, color white;pattern: pattern solid, fore_colour dark_green_ega;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        blue_bold_centre = xlwt.easyxf(
            'font:height 250,bold True;pattern: pattern solid, fore_colour dark_blue_ega;align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        brown_bold_left = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour brown;align: horiz left; borders: top_color black, bottom_color black, right_color black, left_color black,\
                                      left thin, right thin, top thin, bottom thin;')
        bold_left = xlwt.easyxf('font:bold True;align: horiz left')
        bold_right = xlwt.easyxf('font: height 250,bold True;align: horiz right')
        bold_center = xlwt.easyxf('font:bold True;align: horiz center')
        center = xlwt.easyxf('align: horiz center')
        right = xlwt.easyxf('align: horiz right')
        center_gray_shade = xlwt.easyxf('align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,\
                                      left thin, right thin, top thin, bottom thin;')

        font_blue = xlwt.easyxf('pattern: pattern solid, fore_colour white;font: colour blue, bold True;')

        if self.report_type == 'vendor_report':
            sheet = workbook.add_sheet('vendor report')
        else:
            sheet = workbook.add_sheet('products rate report')
        sheet.col(0).width = int(40 * 260)
        sheet.col(1).width = int(60 * 260)
        sheet.col(2).width = int(20 * 260)
        sheet.col(3).width = int(20 * 260)
        sheet.col(4).width = int(20 * 260)
        sheet.col(5).width = int(20 * 260)
        sheet.col(6).width = int(20 * 260)
        sheet.col(7).width = int(20 * 260)
        sheet.row(0).height_mismatch = True
        sheet.row(0).height = 150 * 4

        if self.report_type == 'vendor_report':
            sheet.write_merge(0, 0, 0, 7, 'VENDOR S & F REPORT', lavender_bold_centre)
            col_0_heading = 'VENDORS'
            col_1_heading = 'PRODUCTS'
        else:
            sheet.write_merge(0, 0, 0, 7, 'PRODUCTS S & F REPORT', lavender_bold_centre)
            col_0_heading = 'PRODUCTS'
            col_1_heading = 'VENDORS'
        sheet.write_merge(1, 1, 0, 7, f"Today: {current_date_str}      From:{from_date_str}      To:{to_date_str}",
                          center_gray_shade)

        sheet.row(2).height_mismatch = True
        sheet.row(2).height = 200 * 2

        sheet.write(2, 0, col_0_heading, periwinkle_bold_center)
        sheet.write(2, 1, col_1_heading, periwinkle_bold_center)
        sheet.write(2, 2, 'PO NUM', periwinkle_bold_center)
        sheet.write(2, 3, 'INWARD', periwinkle_bold_center)
        sheet.write(2, 4, 'PASSED', periwinkle_bold_center)
        sheet.write(2, 5, 'FAILED', periwinkle_bold_center)
        sheet.write(2, 6, 'SUCCESS PERCENT', periwinkle_bold_center)
        sheet.write(2, 7, 'FAIL PERCENT', periwinkle_bold_center)

        row = 2
        col = 0
        if len(detail_dict_list) == 0:
            raise ValidationError("No Records within the selected interval.")
        for vend_count, vendor_dict in enumerate(detail_dict_list):
            row += 1
            for key, value in vendor_dict.items():
                sheet.row(row).height_mismatch = True
                sheet.row(row).height = 200 * 2
                if self.report_type == 'product_rate_report':
                    p_or_v_name = self.env['product.template'].search([('name', '=', key)])
                    default_code = f":{p_or_v_name.default_code}" if p_or_v_name.default_code else ""
                else:
                    default_code = ''
                sheet.write_merge(row, row, col, col + 7, f"{vend_count + 1}.{key}{default_code}", sea_green_bold_left)
                for prod_count, prod_id_dict in enumerate(value):
                    for product_id, list_dict in prod_id_dict.items():
                        row += 1
                        if self.report_type == 'vendor_report':
                            p_or_v_name = self.env['product.template'].search([('id', '=', product_id)])
                            default_code = f":{p_or_v_name.default_code}" if p_or_v_name.default_code else ""
                        else:
                            p_or_v_name = self.env['res.partner'].search([('id', '=', product_id)])
                            default_code = ''
                        sheet.row(row).height_mismatch = True
                        sheet.row(row).height = 150 * 2
                        for i, rec in enumerate(list_dict['po_nums_list']):
                            row += 1
                            po = self.env['purchase.order'].search([('id', '=', rec)])
                            sheet.write(row, col + 2, po.name, right)
                            sheet.write(row, col + 3, list_dict['inward_list'][i], right)
                            sheet.write(row, col + 4, list_dict['passed_list'][i], right)
                            sheet.write(row, col + 5, list_dict['failed_list'][i], right)
                            print(f"total:{list_dict['inward_list'][i]}, passed:{list_dict['passed_list'][i]}, "
                                  f"failed:{list_dict['failed_list'][i]}")
                            sheet.write(row, col + 6,
                                        f"{self.get_percent(total=list_dict['inward_list'][i], qty=list_dict['passed_list'][i], po_num=rec)}%", right)
                            sheet.write(row, col + 7,
                                        f"{self.get_percent(total=list_dict['inward_list'][i], qty=list_dict['failed_list'][i], po_num=rec)}%", right)
                        print("out of the for loop")

                        row += 1
                        sheet.row(row).height_mismatch = True
                        sheet.row(row).height = 150 * 5
                        sheet.write(row, col + 1, f"{prod_count + 1}.{p_or_v_name.name}{default_code}", periwinkle_bold_left)
                        passed_list = [num for num in list_dict['passed_list'] if num]
                        failed_list = [num for num in list_dict['failed_list'] if num]
                        print(f"total:{sum(list_dict['inward_list'])}, passed:{sum(passed_list)}, "
                              f"failed:{sum(failed_list)}")
                        # sheet.row(row).height_mismatch = True
                        # sheet.row(row).height = 200 * 2
                        sheet.write(row, col + 3, sum(list_dict['inward_list']), bold_right)
                        sheet.write(row, col + 4, sum(passed_list), bold_right)
                        sheet.write(row, col + 5, sum(failed_list), bold_right)
                        sheet.write(row, col + 6,
                                    f"{self.get_percent(total=sum(list_dict['inward_list']), qty=sum(passed_list))}%", bold_right)
                        sheet.write(row, col + 7,
                                    f"{self.get_percent(total=sum(list_dict['inward_list']), qty=sum(failed_list))}%", bold_right)
                    row += 1

        # fp = BytesIO()
        # workbook.save(fp)
        # self.write(
        #     {'state': 'get', 'file_name': base64.encodebytes(fp.getvalue()), 'summary_data': file_name})
        # fp.close()
        #
        # base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        # attachment_obj = self.env['ir.attachment']
        # if self.report_type == 'vendor_report':
        #     attachment_id = attachment_obj.create(
        #         {'name': f"vendor_report{date.today()}.xls", 'type': 'binary',
        #          'store_fname': f"vendor_report{date.today()}.xls",
        #          'datas': self.file_name}
        #     )
        # else:
        #     attachment_id = attachment_obj.create(
        #         {'name': f"Products_rate_report{date.today()}.xls", 'type': 'binary',
        #          'store_fname': f"products_rate_report{date.today()}.xls",
        #          'datas': self.file_name}
        #     )
        #
        # download_url = f'/web/content/{attachment_id.id}?download=true'
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': str(base_url) + str(download_url),
        #     'target': 'new',
        # }
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)

        file_content = base64.b64encode(fp.getvalue())
        self.write({
            'file_name': file_content,

        })
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=inventory_report&id=%s&field=file_name&download=true&filename={filename}.xls' % (
                self.id),
            'target': 'self'
        }


