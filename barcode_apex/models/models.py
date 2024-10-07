import base64
from odoo.exceptions import ValidationError
from odoo import api, models, fields, _
from datetime import datetime
import qrcode
import io


def give_barcode_as_base64(qr_data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=3, border=4)
    qr.add_data(qr_data)
    # qr.add_data(f"{qr_data['default_code']}~")
    # qr.add_data(f"{qr_data['name']}~")
    qr.make(fit=True)
    img = qr.make_image()
    temp = io.BytesIO()
    img.save(temp, format="PNG")
    qr_image = base64.b64encode(temp.getvalue())
    return qr_image


class CompareDifference(models.TransientModel):
    _name = 'compare.difference'

    product_id = fields.Many2one("product.template", "Product")
    existing_qty = fields.Float("Existing")
    counted_qty = fields.Float("Counted")
    difference = fields.Float("Difference")
    wip_component = fields.Float("WIP as Component")
    wip_product = fields.Float("WIP as Product")
    missing = fields.Float("Missing")
    # state = fields.Selection([('fine', 'Fine'),
    #                          ('mismatch', 'Mismatch')], string='State', compute='compute_state', readonly=True)
    #
    # def compute_state(self):
    #     self.state = 'fine' if self.missing == 0 else 'mismatch'


class Products(models.Model):
    _inherit = 'product.template'

    id_barcode = fields.Binary("Barcode")

    @api.model
    def create(self, vals):
        res = super(Products, self).create(vals)
        print(">>>>>>>>>>>>>>", vals, self.id)
        if vals.get('barcode'):
            qr_data = vals.get('barcode')
        else:
            qr_data = f"{self.id}~{vals.get('default_code')}~{vals.get('name')}"
        qr_image = give_barcode_as_base64(qr_data)
        res['id_barcode'] = qr_image
        return res

    @api.model
    def write(self, vals):
        print("vallllllllllllllllll", vals)
        res = super(Products, self).write(vals)
        if vals.get('barcode'):
            qr_image = give_barcode_as_base64(vals.get('barcode'))
            self.id_barcode = qr_image
        print("resssssssssss", res)
        return res

    def generate_barcodes(self):
        products = self.env['product.template'].search([])
        for product in products:
            product.barcode = f"{product.id}~{product.default_code}~{product.name}"
            # qr_data = {
            #     "id": product.id,
            #     "default_code": product.default_code,
            #     "name": product.name
            # }

            qr_image = give_barcode_as_base64(product.barcode)
            product.update({
                'id_barcode': qr_image
            })
            print("hey hansikk excuse me , this is my number pls text me")


class ScanOverview(models.Model):
    _name = 'scan.overview'

    created_date = fields.Datetime("Created Date", readonly=True)
    ref = fields.Char("Reference")
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done')])
    scan_data_count = fields.Integer("Scans", compute='get_scan_data_count')
    scan_rec_ids = fields.One2many('scan.data', 'overview_id')
    price = fields.Float("price", compute='get_sum_of_product_prices', store=True)
    # total_price = fields.Monetary("Total", compute='get_sum_of_product_prices', store=True, readonly=True,
    #                               digits=(2, 2))

    @api.depends('scan_rec_ids')
    def get_sum_of_product_prices(self):
        for rec in self:
            scan_rec_ids = self.env['scan.data'].search([('overview_id', '=', rec.id)])
            summed_price = 0
            for scan_data in scan_rec_ids:
                summed_price += scan_data.product_id.standard_price
            rec.price = summed_price

    def set_to_draft(self):
        self.state = 'draft'

    def mark_as_done(self):
        self.state = 'done'

    def get_wip(self, product_id):
        stock_move = self.env['stock.move'].search([('location_dest_id', '=', 15),
                                                     ('product_id', '=', product_id),
                                                     ('state', 'not in', ['done', 'cancel'])])
        wip_qty_list = [move.product_uom_qty for move in stock_move]
        component = sum(wip_qty_list)
        stock_move = self.env['stock.move'].search([('location_id', '=', 15),
                                                    ('location_dest_id', '=', 8),
                                                    ('product_id', '=', product_id),
                                                    ('state', 'not in', ['done', 'cancel'])])
        wip_qty_list = [move.product_uom_qty for move in stock_move]
        product = sum(wip_qty_list)
        wip = {
            'component': component,
            'product': product
        }
        return wip

    def compare_inventory(self):
        print("maaradhey mannodu", self.scan_rec_ids)
        if len(self.scan_rec_ids) == 0:
            raise ValidationError("No Scans to compare")
        products = self.env['inventory_report'].products_inventory_details(self.created_date,
                                                                           self.created_date,
                                                                           self.scan_rec_ids,
                                                                           called_from_barcode=True)
        print("productsssssssssss", products)
        compare_difference_list = []
        for idx, val in enumerate(self.scan_rec_ids):
            existing = products[idx]['qty_on_todate']
            print("existing'''''''''''''''''''''''''", type(existing))
            counted = float(val.quantity)
            print("counted''''''''''''''''''''''''''", type(counted))
            wip_component = self.get_wip(val.product_id.id)['component']
            wip_product = self.get_wip(val.product_id.id)['product']
            difference = round(counted - existing, 2)
            missing = difference - wip_component + wip_product
            compare_difference_vals = {
                'product_id': val.product_id.id,
                'existing_qty': existing,
                'counted_qty': counted,
                'difference': difference,
                'wip_component': wip_component,
                'wip_product': wip_product,
                'missing': missing
            }
            compare_difference_list.append(compare_difference_vals)

        print("compare difference list", compare_difference_list)

        self.create_records_in_compare_difference(compare_difference_list)
        print("returnnnukku mela dhaaan irukkan")
        return {
            'name': _(f'Difference Calculation: Date:{self.created_date}'),
            'res_model': 'compare.difference',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('barcode_apex.view_compare_difference_tree').id,
            'target': 'current',
        }

    def create_records_in_compare_difference(self, vals_list):
        print("compare difference", self.env['compare.difference'].search([]))
        inventory_report = self.env['compare.difference'].search([])
        inv_report_id_list = []
        for rec in inventory_report:
            inv_report_id_list.append(rec.id)
        n = len(inv_report_id_list)
        print("length of the list", n)
        # active_id = inv_report_id_list[n-1]
        active_id = self.env.context.get('active_id')
        self.env['compare.difference'].search([('id', '!=', active_id)]).unlink()
        created_records = self.env['compare.difference']
        for vals in vals_list:
            print("recorda also exist")
            record = self.env['compare.difference'].create(vals)
            created_records += record

    def get_scan_data_count(self):
        scan_datas = self.env['scan.data'].search_count([('overview_id', '=', self.id)])
        self.scan_data_count = scan_datas

    def show_scan_datas(self):
        return {
            'name': _('Scans'),
            'view_mode': 'tree,form',
            'res_model': 'scan.data',
            'domain': [('overview_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class ScannedData(models.Model):
    _name = 'scan.data'

    product_id = fields.Many2one("product.template", readonly=[('state', '=', 'done')])
    overview_id = fields.Many2one("scan.overview", readonly=[('state', '=', 'done')])
    internal_ref = fields.Char("Internal Reference", related='product_id.default_code')
    uom_id = fields.Many2one(related='product_id.uom_id')
    quantity = fields.Float("Quantity", default=0, readonly=[('state', '=', 'done')])
    created_date = fields.Datetime("Created Date", readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ], related='overview_id.state')
    category = fields.Many2one(related='product_id.categ_id')
    cost = fields.Float(related='product_id.standard_price', store=True)
    total_price = fields.Float(string='Total Price', compute='_compute_result_column')

    @api.depends('quantity', 'cost')
    def _compute_result_column(self):
        for record in self:
            record.total_price = record.quantity * record.cost
