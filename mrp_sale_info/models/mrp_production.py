
# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools import float_round
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
from collections import defaultdict
from odoo.tools.misc import format_date



# class StockMove(models.Model):
#     _inherit = "stock.move"

    # @api.onchange('actual_consumed_qty', 'store_qty')
    # def onchange_actual_consumed_qty(self):
    #     print("hukum", self.forecast_availability)
    #     if self.store_qty > self.forecast_availability:
    #         raise ValidationError("Store cannot issue greater quantity than available")
    #     if self.actual_consumed_qty > self.store_qty:
    #         raise ValidationError("Consumed quantity cannot be greater than Store issue quantity")
    #     self.move_line_ids.qty_done = self.actual_consumed_qty
    #     self.return_qty = self.store_qty - self.actual_consumed_qty
    #     print("tiger ka hukum", self.move_line_ids.qty_done)

    # store_qty = fields.Float('Store Issue Qty', required=True)
    # actual_consumed_qty = fields.Float('Actual Consumed Qty', required=True)
    # return_qty = fields.Float('Return Qty')

    # @api.depends('product_id', 'picking_type_id', 'picking_id', 'reserved_availability', 'priority', 'state',
    #              'product_uom_qty', 'location_id')
    # def _compute_forecast_information(self):
    #     """ Compute forecasted information of the related product by warehouse."""
    #     self.forecast_availability = False
    #     self.forecast_expected_date = False
    #
    #     # Prefetch product info to avoid fetching all product fields
    #     self.product_id.read(['type', 'uom_id'], load=False)
    #
    #     not_product_moves = self.filtered(lambda move: move.product_id.type != 'product')
    #     for move in not_product_moves:
    #         move.forecast_availability = move.product_qty
    #
    #     product_moves = (self - not_product_moves)
    #
    #     outgoing_unreserved_moves_per_warehouse = defaultdict(set)
    #     now = fields.Datetime.now()
    #
    #     def key_virtual_available(move, incoming=False):
    #         warehouse_id = move.location_dest_id.warehouse_id.id if incoming else move.location_id.warehouse_id.id
    #         return warehouse_id, max(move.date or now, now)
    #
    #     # Prefetch efficiently virtual_available for _consuming_picking_types draft move.
    #     prefetch_virtual_available = defaultdict(set)
    #     virtual_available_dict = {}
    #     for move in product_moves:
    #         if (move.picking_type_id.code in self._consuming_picking_types() or move._is_inter_wh()) and move.state == 'draft':
    #             prefetch_virtual_available[key_virtual_available(move)].add(move.product_id.id)
    #         elif move.picking_type_id.code == 'incoming':
    #             prefetch_virtual_available[key_virtual_available(move, incoming=True)].add(move.product_id.id)
    #     for key_context, product_ids in prefetch_virtual_available.items():
    #         read_res = self.env['product.product'].browse(product_ids).with_context(warehouse=key_context[0], to_date=key_context[1]).read(['virtual_available'])
    #         virtual_available_dict[key_context] = {res['id']: res['virtual_available'] for res in read_res}
    #
    #     for move in product_moves:
    #         if move.picking_type_id.code in self._consuming_picking_types() or move._is_inter_wh():
    #             if move.state == 'assigned':
    #                 move.forecast_availability = move.product_uom._compute_quantity(
    #                     move.reserved_availability, move.product_id.uom_id, rounding_method='HALF-UP')
    #             elif move.state == 'draft':
    #                 # for move _consuming_picking_types and in draft -> the forecast_availability > 0 if in stock
    #                 move.forecast_availability = virtual_available_dict[key_virtual_available(move)][move.product_id.id] - move.product_qty
    #             elif move.state in ('waiting', 'confirmed', 'partially_available'):
    #                 outgoing_unreserved_moves_per_warehouse[move.location_id.warehouse_id].add(move.id)
    #         elif move.picking_type_id.code == 'incoming':
    #             forecast_availability = virtual_available_dict[key_virtual_available(move, incoming=True)][move.product_id.id]
    #             if move.state == 'draft':
    #                 forecast_availability += move.product_qty
    #             move.forecast_availability = forecast_availability
    #
    #     for warehouse, moves_ids in outgoing_unreserved_moves_per_warehouse.items():
    #         if not warehouse:  # No prediction possible if no warehouse.
    #             continue
    #         moves = self.browse(moves_ids)
    #         forecast_info = moves._get_forecast_availability_outgoing(warehouse)
    #         for move in moves:
    #             move.forecast_availability, move.forecast_expected_date = forecast_info[move]


class CustomStockInventoryReport(models.TransientModel):
    _name = 'custom.stock.inventory.report'

    start_date = fields.Date('Start Dare', required=True)
    end_date = fields.Date('End Dare', required=True)
    filter_by = fields.Selection([('product', 'Product'), ('order', 'Order')], default='product', string="Filter By")
    workorder_ids = fields.Many2many('mrp.production', string="Order")
    product_ids = fields.Many2many('product.product', string="Product")


    @api.onchange('filter_by')
    def get_proper_data(self):
        if self.filter_by:
            if self.filter_by == 'product':
                self.workorder_ids = False
            if self.filter_by == 'order':
                self.product_ids = False

    def action_print(self):
        return self.env.ref('mrp_sale_info.report_inventory_transfer_report').report_action(self)

    def _get_report_base_filename(self):
        return 'Inventory Transfer Report' + '_' + str(self.start_date) + ' To ' + str(self.end_date)


class StockInventoryTransferReport(models.AbstractModel):
    _name = 'report.mrp_sale_info.inventory_transfer_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        worksheet = workbook.add_worksheet('Inventory Transfer Report')
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        col = workbook.add_format({'align': 'left', 'bold': 1, "align": "center", "border": 1, "bg_color": "#87CEEB"})
        col_2 = workbook.add_format({'align': 'left', 'bold': 1, "align": "center", "border": 1})
        col_1 = workbook.add_format({'align': 'left', "border": 1})
        my_format = workbook.add_format({'align': 'right', 'num_format': '0.00', "border": 1, 'bold': 1})

        new = obj.start_date.strftime('%Y-%m-%d 00:00:00')
        new_1 = obj.end_date.strftime('%Y-%m-%d 23:23:59')

        row = 0
        if obj.filter_by == 'product':
            row = 1
            worksheet.write('A%s' % (row), 'Work Order No', col)
            worksheet.write('B%s' % (row), 'Product', col)
            worksheet.write('C%s' % (row), 'Reserved', col)
            # worksheet.write('D%s' % (row), 'Store Issue', col)
            worksheet.write('E%s' % (row), 'Consumed', col)
            # worksheet.write('F%s' % (row), 'Actual Consumed', col)
            # worksheet.write('G%s' % (row), 'Returned Quantity', col)
            row += 1
            search_domain = [('date_planned_start', '>=', new),
                             ('date_planned_start', '<=', new_1)]
            mrp_production_rec = self.env['mrp.production'].search(search_domain)
            total_reserved = 0
            total_store = 0
            total_product = 0
            total_actual = 0
            total_return = 0
            for rec in mrp_production_rec:
                for move in rec.move_raw_ids:
                    if move.product_id.id in obj.product_ids.ids:
                        worksheet.write('A%s' % (row), rec.name or '', col_1)
                        worksheet.write('B%s' % (row), move.product_id.display_name or '', col_1)
                        worksheet.write('C%s' % (row), move.forecast_availability or 0, my_format)
                        # worksheet.write('D%s' % (row), move.store_qty or 0, my_format)
                        worksheet.write('E%s' % (row), move.product_uom_qty or 0, my_format)
                        # worksheet.write('F%s' % (row), move.actual_consumed_qty or 0, my_format)
                        # worksheet.write('G%s' % (row), move.return_qty or 0, my_format)
                        row += 1
                        total_reserved = total_reserved + move.forecast_availability
                        # total_store = total_store + move.store_qty
                        total_product = total_product + move.product_uom_qty
                        # total_actual = total_actual + move.actual_consumed_qty
                        # total_return = total_return + move.return_qty
            worksheet.write('A%s' % (row), 'Total', col_2)
            worksheet.write('B%s' % (row), '', col)
            worksheet.write('C%s' % (row), total_reserved or 0, my_format)
            worksheet.write('D%s' % (row), total_store or 0, my_format)
            worksheet.write('E%s' % (row), total_product or 0, my_format)
            worksheet.write('F%s' % (row), total_actual or 0, my_format)
            worksheet.write('G%s' % (row), total_return or 0, my_format)
        if obj.filter_by == 'order':
            search_domain = [('date_planned_start', '>=', new),
                             ('date_planned_start', '<=', new_1), ('id', 'in', obj.workorder_ids.ids)]
            mrp_production_rec = self.env['mrp.production'].search(search_domain)
            for rec in mrp_production_rec:
                worksheet.merge_range(row, 0, row, 6, rec.name, col)
                row += 2
                worksheet.write('A%s' % (row), 'Work Order No', col)
                worksheet.write('B%s' % (row), 'Product', col)
                worksheet.write('C%s' % (row), 'Reserved', col)
                worksheet.write('D%s' % (row), 'Store Issue', col)
                worksheet.write('E%s' % (row), 'Consumed', col)
                worksheet.write('F%s' % (row), 'Actual Consumed', col)
                worksheet.write('G%s' % (row), 'Returned Quantity', col)
                row += 1
                total_reserved = 0
                total_store = 0
                total_product = 0
                total_actual = 0
                total_return = 0
                for move in rec.move_raw_ids:
                    worksheet.write('A%s' % (row), rec.name or '', col_1)
                    worksheet.write('B%s' % (row), move.product_id.display_name or '', col_1)
                    worksheet.write('C%s' % (row), move.forecast_availability or 0, my_format)
                    # worksheet.write('D%s' % (row), move.store_qty or 0, my_format)
                    worksheet.write('E%s' % (row), move.product_uom_qty or 0, my_format)
                    # worksheet.write('F%s' % (row), move.actual_consumed_qty or 0, my_format)
                    # worksheet.write('G%s' % (row), move.return_qty or 0, my_format)
                    row += 1
                    total_reserved = total_reserved + move.forecast_availability
                    # total_store = total_store + move.store_qty
                    total_product = total_product + move.product_uom_qty
                    # total_actual = total_actual + move.actual_consumed_qty
                    # total_return = total_return + move.return_qty
                worksheet.write('A%s' % (row), 'Total', col_2)
                worksheet.write('B%s' % (row), '', col)
                worksheet.write('C%s' % (row), total_reserved or 0, my_format)
                worksheet.write('D%s' % (row), total_store or 0, my_format)
                worksheet.write('E%s' % (row), total_product or 0, my_format)
                worksheet.write('F%s' % (row), total_actual or 0, my_format)
                worksheet.write('G%s' % (row), total_return or 0, my_format)
                row += 2


class BillMaterial(models.Model):
    _inherit = 'mrp.bom'

    product_pack = fields.Many2one('product.product')
    pack_qty = fields.Float('Pack Qty')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    _order = 'id desc'

    @api.onchange('qty_producing')
    def onchange_qty_producing(self):
        print("i have been called")
        for line in self.move_raw_ids:
            print("line.forecast_availability", line.forecast_availability)
            availability = line.forecast_availability
            should_consume = line.should_consume_qty
            if availability >= should_consume:
                can_consume = should_consume
            else:
                can_consume = availability
            # line.actual_consumed_qty = can_consume
            # line.store_qty = can_consume
            # line.return_qty = line.store_qty - line.actual_consumed_qty

    product_pack = fields.Many2one('product.product', related='bom_id.product_pack')
    pack_qty = fields.Float('Pack Qty', compute='compute_pack_qty')
    move_pack_transfer_count = fields.Integer(compute='pack_used_count', store=True)
    draw_num = fields.Char(string='Drawing Number')
    revision = fields.Char(string='Revision')
    program_number = fields.Char(string='Program Number')

    @api.onchange('product_qty', 'bom_id')
    def _onchange_pack_qty(self):
        if self.product_qty or self.bom_id:
            for line in self:
                if line.product_qty and line.bom_id:
                    line.pack_qty = int(line.product_qty * line.bom_id.pack_qty)
                else:
                    line.pack_qty = int(line.bom_id.pack_qty)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # self.bom_id = self.env['mrp.bom']._bom_find(products=self.product_id, company_id=self.company_id.id)
            self.draw_num = self.product_id.drawing_number
            self.revision = self.product_id.revision
            self.program_number = self.product_id.product_tmpl_id.program_number

    @api.depends('state')
    def pack_used_count(self):
        for m_line in self:
            move_branch_mrp_pick_id = self.env['stock.picking'].search([('mrp_pack_id', '=', m_line.id)])
            if move_branch_mrp_pick_id:
                m_line.move_pack_transfer_count = len(move_branch_mrp_pick_id)

    def open_view_pack_done_picking(self):
        tree_view_id = self.env.ref('stock.vpicktree').id
        form_view_id = self.env.ref('stock.view_picking_form').id
        return {
            'name': _('Stock'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': self._context,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('mrp_pack_id', '=', self.id)]
        }

    # def button_mark_done(self):
    #     for line in self.move_raw_ids:
    #         if not line.store_qty:
    #             raise ValidationError('"Store Issue Quantity" Cannot Be Null ')
    #         if not line.actual_consumed_qty:
    #             raise ValidationError('Actual Consumed Quantity" Cannot Be Null ')
    #         if line.actual_consumed_qty > line.store_qty:
    #             raise ValidationError("'Consumed quantity' should not exceed the 'Store issue Quantity'")
    #         # line.old_available_qty=line.available_qty
    #     res = super(MrpProduction, self).button_mark_done()
    #     if res == True:
    #         if self.product_pack and self.pack_qty <= 0:
    #             raise ValidationError('"Packaging Quantity" Cannot Be Null ')
    #         # if not self.product_pack:
    #         #     raise ValidationError('Packaging Product Should Be Greater Than Zero ')
    #         if self.product_pack:
    #             picking_obj = self.env['stock.picking']
    #             move_obj = self.env['stock.move']
    #             group_id = self.env['procurement.group'].create({
    #                 'name': self.name, 'move_type': 'one',
    #             })
    #             cus_location_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)
    #             # ven_location_id = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1)
    #             picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
    #             # picking_ven_type_id = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
    #
    #             quant_id = self.env['stock.quant'].search(
    #                 [('product_id', '=', self.product_pack.id), ('location_id', '=', self.location_dest_id.id)])
    #
    #             if quant_id:
    #                 if quant_id.quantity > 0:
    #                     pass
    #                 else:
    #                     raise ValidationError('You Dont Have Packing Stock !!')
    #             vals = {
    #                 'picking_type_id': picking_type_id.id,
    #                 'date': fields.Datetime.now(),
    #                 'origin': self.name,
    #                 'location_dest_id': cus_location_id.id,
    #                 'location_id': self.location_dest_id.id,
    #                 'company_id': self.env.user.company_id.id,
    #                 'group_id': group_id.id,
    #                 'mrp_pack_id': self.id
    #             }
    #             picking_id_1 = picking_obj.sudo().create(vals)
    #             print(picking_id_1)
    #             move_list_1 = []
    #             move_vals_1 = {
    #                 'name': self.name,
    #                 'product_id': self.product_pack.id,
    #                 'product_uom': self.product_id.uom_id.id,
    #                 'product_uom_qty': float(self.pack_qty),
    #                 # 'date': sched_date_val,
    #                 'location_id': self.location_dest_id.id,
    #                 'location_dest_id': cus_location_id.id,
    #                 'picking_id': picking_id_1.id,
    #                 'company_id': self.env.user.company_id.id,
    #                 'picking_type_id': picking_type_id.id,
    #                 'group_id': group_id.id,
    #                 'origin': picking_id_1.name,
    #             }
    #             move_list_1.append(move_vals_1)
    #             move_id_1 = move_obj.sudo().create(move_list_1)
    #             print(move_id_1)
    #             picking_id_1.sudo().action_confirm()
    #             picking_id_1.sudo().action_assign()
    #             for move_id in picking_id_1.move_ids_without_package:
    #                 move_id.quantity_done = move_id.product_uom_qty
    #             picking_id_1.sudo().button_validate()
    #
    #     return res

    def compute_pack_qty(self):
        if self.product_qty:
            for rec in self:
                if rec.product_qty:
                    rec.pack_qty = rec.product_qty * rec.bom_id.pack_qty
                    split = str(rec.pack_qty).split('.')
                    int_part = int(split[0])
                    decimal_part = int(split[1])
                    if decimal_part > 0:
                        int_part += 1
                        print("int................", int_part)
                        rec.pack_qty = int_part

                else:
                    rec.pack_qty = round(rec.bom_id.pack_qty)
                    print("else part.........", rec.bom_id.pack_qty)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mrp_pack_id = fields.Many2one('mrp.production')



