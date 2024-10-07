from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta, time
from odoo import api, models, fields, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError, ValidationError


def compute_of_uom_qty(purchase_line):
    for line in purchase_line:
        print("shaggy", line)
        received = line.product_uom._compute_quantity(line.qty_received, line.product_uom, round=False)
        product_uom_qty = line.product_uom_qty
        line.uom_qty = product_uom_qty - received


class QualityCheck(models.Model):
    _name = 'quality.apex'

    def default_get(self, fields):
        res = super(QualityCheck, self).default_get(fields)
        res['qc_name'] = self.env.user.name
        return res

    name = fields.Char(readonly=True, copy=False)
    stock_move = fields.Many2one('stock.move')
    qc_name = fields.Char("Quality Checker", readonly=True)
    product_id = fields.Many2one("product.template", "Product", readonly=True)
    product_uom_id = fields.Many2one("uom.uom", readonly=True)
    po_num = fields.Many2one('purchase.order', string="PO NUM", readonly=True)
    trans_ref = fields.Many2one('stock.picking', string="Transfer", readonly=True)
    vendor_id = fields.Many2one("res.partner", string='Vendor', readonly=True)
    created_date = fields.Datetime("Created Date", readonly=True)
    approved_date = fields.Datetime("Approved Date", readonly=True)
    pass_ref = fields.Many2one('stock.picking', string="Pass Reference", readonly=True)
    fail_ref = fields.Many2one('stock.picking', string="Fail Reference", readonly=True)
    pass_trans_id = fields.Integer()
    fail_trans_id = fields.Integer()
    quantity = fields.Float("Inward", digits=(12, 6), related='stock_move.quantity', store=True)
    passed = fields.Float("Passed", digits=(12, 6))
    failed = fields.Float("Failed", digits=(12, 6))
    state = fields.Selection([('checking', "Checking"),
                              ('done', "Done")], default='checking', readonly=True)
    is_locked = fields.Boolean(default=False)

    def create_records(self, move_id):
        from datetime import datetime
        # for line_id in stock_move_line_ids_list:
        stock_move = self.env['stock.move'].search([('id', '=', move_id)])
        print("..........stock move status'", stock_move.state)

        picking = self.env['stock.picking'].search([('id', '=', stock_move.picking_id.id)])
        print("line id $$$$$$$$$$.purchase line id", stock_move.purchase_line_id.order_id)
        po = self.env['purchase.order'].search([('id', '=', stock_move.purchase_line_id.order_id.id)])
        self.create({
            'name': self.env['ir.sequence'].next_by_code('quality.apex'),
            'stock_move': stock_move.id,
            'product_id': stock_move.product_id.id,
            'vendor_id': picking.partner_id.id,
            'product_uom_id': stock_move.product_uom.id,
            'po_num': po.id,
            'trans_ref': picking.id,
            'quantity': stock_move.quantity,
            'created_date': datetime.today()
        })

    def create_transfer_to_stock(self):
        from datetime import datetime
        operation_type = self.env.ref('quality.operation_type_qc_to_stock')
        print("varavathi erakkam amaron vandhu ninna sirakkum", self.stock_move.price_unit)
        draft_transfer = self.env['stock.picking'].create({
            'partner_id': self.vendor_id.id,
            'picking_type_id': operation_type.id,
            'location_id': operation_type.default_location_src_id.id,
            'location_dest_id': operation_type.default_location_dest_id.id,
            'scheduled_date': datetime.today(),
            'origin': self.name,
            'move_ids_without_package': [(0, 0, {
                'name': self.product_id.name,
                'product_id': self.product_id.id,
                'product_uom_qty': self.passed,
                'origin': self.name,
                'warehouse_id': 1,
                'location_id': operation_type.default_location_src_id.id,
                'location_dest_id': operation_type.default_location_dest_id.id,
                'price_unit': self.stock_move.price_unit,
                'product_uom': self.product_uom_id.id,
            })]
        })
        return draft_transfer

    def create_return_for_fails(self):
        # stock_move_line = self.env['stock.move.line'].search(
        #     [('picking_id', '=', self.trans_ref.id), ('product_id', '=', self.product_id.id)])
        vals = {
            'product_id': self.product_id.id,
            'quantity': self.failed,
            'uom_id': self.product_uom_id.id,
            'move_id': self.stock_move.id,
            'to_refund': True,
        }
        stock_re_pick = self.env['stock.return.picking'].create({
            'product_return_moves': [(0, 0, vals)],
            'location_id': 4
        })
        return_pick_id, operation_type_id = stock_re_pick._create_returns(pick=self.trans_ref,
                                                                          stock_re_pick=stock_re_pick)
        return return_pick_id

    def approve(self):
        valid_pass_qty = self.quantity - self.failed
        if self.passed > round(valid_pass_qty, 2):
            raise UserError("Entered Passed Quantity is not valid")
        valid_fail_qty = self.quantity - self.passed
        if self.failed > round(valid_fail_qty, 2):
            raise UserError("Entered Failed quantity is not Valid")
        print(f"++++++++++++{len(self.pass_ref)},************* {self.fail_ref}")
        from datetime import datetime
        self.approved_date = datetime.today()
        if self.passed != 0 and len(self.pass_ref) == 0:
            print("todoooooo1")
            draft_transfer = self.create_transfer_to_stock()
            print("todoooooo2")
            draft_transfer.action_confirm()
            print("todoooooo3", draft_transfer.name, "....")
            draft_transfer.action_assign()
            print("todoooooooo4", draft_transfer.id)
            for line in draft_transfer.move_line_ids_without_package:
                print("has a work here")
                line.quantity = line.quantity_product_uom
            draft_transfer.button_validate()
            self.pass_ref = draft_transfer.id
        elif len(self.pass_ref) == 1:
            stock_move = self.env['stock.move'].search([('product_id', '=', self.product_id.id),
                                                        ('picking_id', '=', self.pass_ref.id)])
            stock_move_line = self.env['stock.move.line'].search([('move_id', '=', stock_move.id)])
            stock_move_line.quantity = self.passed
            vals = {
                'product_uom_qty': self.passed,
                'quantity': self.passed
            }
            self.pass_ref.write({'move_ids_without_package': [(1, stock_move.id, vals)]})

        if self.failed != 0 and len(self.fail_ref) == 0:
            self.fail_ref = self.create_return_for_fails()
            stock_move = self.env['stock.move'].search(
                [('product_id', '=', self.product_id.id), ('picking_id', '=', self.fail_ref.id)])
            # stock_move.change_actual_qty = True
            stock_move_line = self.env['stock.move.line'].search([('move_id', '=', stock_move.id)])

            stock_move_line.quantity_product_uom = stock_move.product_uom_qty
            stock_move_line.quantity = stock_move_line.quantity_product_uom
            # wizard = self.env['stock.move.line.wizard'].create({
            #     'picking': self.fail_ref.id,
            #     'stock_line_ids': [(4, stock_move_line.id)]
            # })
            # print('wizard', wizard)
            # wizard.validate()
            self.fail_ref.button_validate()
            self.env['purchase.order'].change_status(po_num=self.po_num.name, partial=True)
            stock_move = self.env['stock.move'].search(
                [('picking_id', '=', self.fail_ref.id), ('product_id', '=', self.product_id.id)])
            # stock_move.change_uom_stock_qty = False

            # print('minni', stock_move.purchase_line_id)
            # self.env['purchase.order.line'].received_quantity_computation(stock_move.purchase_line_id.id)
            print("......rataata raa ta rata rata ta")
            print("............fodjfsdofdjfo")
            # stock_move.purchase_line_id.compute_uom_qty()
        elif len(self.fail_ref) == 1:
            stock_move = self.env['stock.move'].search(
                [('product_id', '=', self.product_id.id), ('picking_id', '=', self.fail_ref.id)])
            stock_move_line = self.env['stock.move.line'].search([('move_id', '=', stock_move.id)])
            if self.fail_ref.state == 'done':
                print("stock move line.quty done")
                stock_move_line.quantity = self.failed

        self.is_locked = True
        if round(self.passed, 2) + round(self.failed, 2) == round(self.quantity, 2):
            self.state = 'done'
            po = self.env['purchase.order'].search([('id', '=', self.po_num.id)])
            po_line = self.env['purchase.order.line'].search([('order_id', '=', po.id)])
            # compute_of_uom_qty(po_line)
            qc = self.env['quality.apex'].search([('po_num', '=', po.id), ('state', '=', 'done')])
            product_ids = []
            for rec in qc:
                if rec.product_id.id not in product_ids:
                    product_ids.append(rec.product_id.id)
            po.no_of_quality_done_items = len(product_ids)
            print("........print no of quality done items", len(product_ids))
            po.change_status(po.name)

    def unlock(self):
        self.is_locked = False


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self, from_backorder=False):
        self.write({})
        print(".........dum dum dum padikadum", self.id)
        origin = self.origin
        # picking_id = self.env['stock.picking'].search([('id', '=', self.id)])


        draft_picking = self.filtered(lambda p: p.state == 'draft')
        draft_picking.action_confirm()
        for move in draft_picking.move_ids:
            if float_is_zero(move.quantity, precision_rounding=move.product_uom.rounding) and \
                    not float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                move.quantity = move.product_uom_qty

        # Sanity checks.
        if not self.env.context.get('skip_sanity_check', False):
            self._sanity_check()
        self.message_subscribe([self.env.user.partner_id.id])

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        pickings_not_to_backorder = self.filtered(lambda p: p.picking_type_id.create_backorder == 'never')
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
                lambda p: p.picking_type_id.create_backorder != 'always'
            )
        pickings_to_backorder = self - pickings_not_to_backorder
        # print("..........origin",origin)
        print("........pickings_to_backorder.", pickings_to_backorder)
        print("........pickings_not toto_backorder.", pickings_not_to_backorder)
        if len(pickings_to_backorder) > 0:
            print("backorder create panna poren", pickings_to_backorder.id)
            stock_move = self.env['stock.move'].search([('picking_id', '=', pickings_to_backorder.id)])
            for line in stock_move:
                print(f"stock move.id", line.id, "is_done:", line.is_done, "state:", line.state)
                if self.location_dest_id.id == 22 and line.state != 'confirmed':
                    print("beat me; hate me; you can never break me;")
                    self.env['quality.apex'].create_records(line.id)
                # line.change_actual_qty = True
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
        if not from_backorder:
            self.env['purchase.order'].change_status(origin, complete=True)
        # if len(pickings_not_to_backorder) == 0 and len(pickings_to_backorder) == 0:
        #     self.env['purchase.order'].change_status(origin, complete=True)
        # elif len(pickings_not_to_backorder) == 0 and len(pickings_to_backorder) != 0:
        #     self.env['purchase.order'].change_status(origin, partial=True)
        # po = self.env['purchase.order'].search([('name', '=', origin)])
        # po_lines = self.env['purchase.order.line'].search([('order_id', '=', po.id)])
        # for po_line in po_lines:
        #     self.env['purchase.order.line'].received_quantity_computation(po_line.id)
        report_actions = self._get_autoprint_report_actions()
        another_action = False
        if self.user_has_groups('stock.group_reception_report'):
            pickings_show_report = self.filtered(lambda p: p.picking_type_id.auto_show_reception_report)
            lines = pickings_show_report.move_ids.filtered(
                lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location']._search(
                    [('id', 'child_of', pickings_show_report.picking_type_id.warehouse_id.view_location_id.ids),
                     ('usage', '!=', 'supplier')])
                if self.env['stock.move'].search([
                    ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                    ('product_qty', '>', 0),
                    ('location_id', 'in', wh_location_ids),
                    ('move_orig_ids', '=', False),
                    ('picking_id', 'not in', pickings_show_report.ids),
                    ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = pickings_show_report.action_view_reception_report()
                    action['context'] = {'default_picking_ids': pickings_show_report.ids}
                    if not report_actions:
                        return action
                    another_action = action
        if report_actions:
            return {
                'type': 'ir.actions.client',
                'tag': 'do_multi_print',
                'params': {
                    'reports': report_actions,
                    'anotherAction': another_action,
                }
            }
        return True

#


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_move_default_values(self, return_line, new_picking, is_called_from_custom_code=False):
        if is_called_from_custom_code:
            print(f"return_line:{return_line}\nnew_picking:{new_picking}")
            vals = {
                'product_id': return_line.product_id.id,
                'product_uom_qty': return_line.quantity,
                'uom_stock_qty': return_line.quantity,
                'product_uom': return_line.product_id.uom_id.id,
                'picking_id': new_picking.id,
                'state': 'draft',
                'date': fields.Datetime.now(),
                'location_id': return_line.move_id.location_dest_id.id,
                'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
                'picking_type_id': new_picking.picking_type_id.id,
                'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
                'origin_returned_move_id': return_line.move_id.id,
                'to_refund': True if new_picking.picking_type_id.code == 'outgoing' else False,
                # 'change_uom_stock_qty': True,
                'procure_method': 'make_to_stock',
            }
            if new_picking.picking_type_id.code == 'outgoing':
                vals['partner_id'] = new_picking.partner_id.id
            return vals
        else:
            print("called from source")
            vals = {
                'product_id': return_line.product_id.id,
                'product_uom_qty': return_line.quantity,
                'product_uom': return_line.product_id.uom_id.id,
                'picking_id': new_picking.id,
                'state': 'draft',
                'date': fields.Datetime.now(),
                'location_id': return_line.move_id.location_dest_id.id,
                'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
                'picking_type_id': new_picking.picking_type_id.id,
                'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
                'origin_returned_move_id': return_line.move_id.id,
                'procure_method': 'make_to_stock',
            }
            if new_picking.picking_type_id.code == 'outgoing':
                vals['partner_id'] = new_picking.partner_id.id
            return vals

    def _create_returns(self, pick=False, stock_re_pick=False):
        line_fields = [f for f in self.env['stock.return.picking.line']._fields.keys()]
        product_return_moves_data_tmpl = self.env['stock.return.picking.line'].default_get(line_fields)
        for line in self.picking_id.move_line_ids_without_package:
            product_return_moves_data = dict(product_return_moves_data_tmpl)
            product_return_moves_data.update(self._prepare_stock_return_picking_line_vals_from_move(line.move_id))
            self.product_return_moves = [(0, 0, product_return_moves_data)]
        # TODO sle: the unreserve of the next moves could be less brutal
        if pick and stock_re_pick:
            print("thak thathin thathin", pick, ".........", pick.id)
            for return_move in stock_re_pick.product_return_moves.mapped('move_id'):
                return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

            # create new picking for returned products
            print("...........5%%%%%%%%%%", self, "222", self.picking_id, '00000000000000', stock_re_pick)
            print("nara nara nagara nagara pala pala naringa nerunga viru viru venga iranga")
            new_picking = pick.copy({
                'move_ids': [],
                'picking_type_id': pick.picking_type_id.return_picking_type_id.id,
                'state': 'draft',
                'origin': _("Return of %s", pick.name),
                'location_id': pick.location_dest_id.id,
                'location_dest_id': stock_re_pick.location_id.id})
            print(".......yeno.............", new_picking)
            picking_type_id = new_picking.picking_type_id.id
            new_picking.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': new_picking, 'origin': stock_re_pick.picking_id},
                subtype_xmlid='mail.mt_note',
            )
            print("ekit tho edki thdfksfkjsdhf")
            returned_lines = 0
            for return_line in stock_re_pick.product_return_moves:
                print("yagi yagi yagi yaagi")
                if not return_line.move_id:
                    raise UserError(_("You have manually created product lines, please delete them to proceed."))
                if not float_is_zero(return_line.quantity, precision_rounding=return_line.uom_id.rounding):
                    returned_lines += 1
                    vals = stock_re_pick._prepare_move_default_values(return_line, new_picking, is_called_from_custom_code=True)
                    r = return_line.move_id.copy(vals)
                    vals = {}

                    # +--------------------------------------------------------------------------------------------------------+
                    # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                    # |              | returned_move_ids              ↑                                  | returned_move_ids
                    # |              ↓                                | return_line.move_id              ↓
                    # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                    # +--------------------------------------------------------------------------------------------------------+
                    move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                    # link to original move
                    move_orig_to_link |= return_line.move_id
                    # link to siblings of original move, if any
                    move_orig_to_link |= return_line.move_id\
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))\
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                    move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                    # link to children of originally returned moves, if any. Note that the use of
                    # 'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
                    # instead of 'return_line.move_id.move_orig_ids.move_dest_ids' prevents linking a
                    # return directly to the destination moves of its parents. However, the return of
                    # the return will be linked to the destination moves.
                    move_dest_to_link |= return_line.move_id.move_orig_ids.mapped('returned_move_ids')\
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))\
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                    vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                    vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                    r.write(vals)
            if not returned_lines:
                raise UserError(_("Please specify at least one non-zero quantity."))

            new_picking.action_confirm()
            new_picking.action_assign()
            return new_picking.id, picking_type_id
        else:
            print("moota thooku mamoi")
            for return_move in self.product_return_moves.mapped('move_id'):
                return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

            # create new picking for returned products
            new_picking = self.picking_id.copy(self._prepare_picking_default_values())
            picking_type_id = new_picking.picking_type_id.id
            new_picking.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': new_picking, 'origin': self.picking_id},
                subtype_xmlid='mail.mt_note',
            )
            returned_lines = 0
            for return_line in self.product_return_moves:
                if not return_line.move_id:
                    raise UserError(_("You have manually created product lines, please delete them to proceed."))
                if not float_is_zero(return_line.quantity, precision_rounding=return_line.uom_id.rounding):
                    returned_lines += 1
                    vals = self._prepare_move_default_values(return_line, new_picking)
                    r = return_line.move_id.copy(vals)
                    vals = {}

                    # +--------------------------------------------------------------------------------------------------------+
                    # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                    # |              | returned_move_ids              ↑                                  | returned_move_ids
                    # |              ↓                                | return_line.move_id              ↓
                    # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                    # +--------------------------------------------------------------------------------------------------------+
                    move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                    # link to original move
                    move_orig_to_link |= return_line.move_id
                    # link to siblings of original move, if any
                    move_orig_to_link |= return_line.move_id \
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel')) \
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                    move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                    # link to children of originally returned moves, if any. Note that the use of
                    # 'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
                    # instead of 'return_line.move_id.move_orig_ids.move_dest_ids' prevents linking a
                    # return directly to the destination moves of its parents. However, the return of
                    # the return will be linked to the destination moves.
                    move_dest_to_link |= return_line.move_id.move_orig_ids.mapped('returned_move_ids') \
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel')) \
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                    vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                    vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                    r.write(vals)
            if not returned_lines:
                raise UserError(_("Please specify at least one non-zero quantity."))

            new_picking.action_confirm()
            new_picking.action_assign()
            # stock_moves = self.env['stock.move'].search([('picking_id', '=', self.picking_id.id)])
            # for stock_move in stock_moves:
            #     po_line = stock_move.purchase_line_id
            #     print("call call receivied quantiyt computation")
            #     po_line.received_quantity_computation(po_line.id)
            return new_picking.id, picking_type_id


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Need To Receive'),
        ('partial', 'Partially Received'),
        ('complete_receive', 'Quality'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    no_of_quality_done_items = fields.Integer()

    def change_status(self, po_num, partial=False, complete=False):
        print(f"change status called with,ponum: {po_num} partial: {partial}, complete: {complete}")
        po = self.env['purchase.order'].search([('name', '=', po_num)])
        actual_sum = sum(po.order_line.mapped('product_qty'))
        received_sum = sum(po.order_line.mapped('qty_received'))
        no_of_line_items = len(list(po.order_line))
        print("actual sum.....%%%%%%%%%%%%%.", actual_sum)
        print("received sum...%%%%%%%%%%%%..", received_sum)
        if partial:
            po.state = 'partial'
        elif complete:
            po.state = 'complete_receive'
        elif no_of_line_items == self.no_of_quality_done_items and po.state == 'complete_receive':
            if round(actual_sum, 2) == round(received_sum, 2):
                po.state = 'done'
            else:
                po.state = 'partial'


class StockBackorderConfirmation(models.TransientModel):
    _inherit = "stock.backorder.confirmation"

    def process(self):
        print("vizhundhal vidhayai elundhal malaiyai thalaivan oruvan peruvan perum porkalaigyan")
        pickings_to_do = self.env['stock.picking']
        pickings_not_to_do = self.env['stock.picking']
        for line in self.backorder_confirmation_line_ids:
            if line.to_backorder is True:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id

        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate).with_context(
                skip_backorder=True)
            print("self.env.contectllllllllllll", self.env.context)
            ctx = self.env.context

            origin = ctx.get('default_origin')
            if origin == None:
                picking_id = ctx['active_id']
                picking = self.env['stock.picking'].search([('id', '=', picking_id)])
                origin_with_return_of = picking.origin
                origin_of_picking = origin_with_return_of.replace('Return of ', "")
                picking_with_po_as_origin = self.env['stock.picking'].search([('name', '=', origin_of_picking)])
                origin = picking_with_po_as_origin.origin

            self.env['purchase.order'].change_status(origin, partial=True)
            print("create_backorder")
            # po = self.env['purchase.order'].search([('name', '=', origin)])
            # po_lines = self.env['purchase.order.line'].search([('order_id', '=', po.id)])
            # for po_line in po_lines:
            #     self.env['purchase.order.line'].received_quantity_computation(po_line.id)
            if pickings_not_to_do:
                self._check_less_quantities_than_expected(pickings_not_to_do)
                pickings_to_validate = pickings_to_validate.with_context(
                    picking_ids_not_to_backorder=pickings_not_to_do.ids)
            return pickings_to_validate.button_validate(from_backorder=True)
        ctx = self.env.context
        print("self.env.contectllllllllllll", self.env.context)
        origin = ctx['default_origin']
        print("thalaivan oruvan perum por kalai gyan")
        self.env['purchase.order'].change_status(origin, partial=True)
        # po = self.env['purchase.order'].search([('name', '=', origin)])
        # po_lines = self.env['purchase.order.line'].search([('order_id', '=', po.id)])
        # for po_line in po_lines:
        #     self.env['purchase.order.line'].received_quantity_computation(po_line.id)
        return True

    def process_cancel_backorder(self):
        pickings_to_validate_ids = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate_ids:
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate_ids)
            self._check_less_quantities_than_expected(pickings_to_validate)
            ctx = self.env.context
            origin = ctx['default_origin']
            print("cancel backorder")
            self.env['purchase.order'].change_status(origin, complete=True)
            # po = self.env['purchase.order'].search([('name', '=', origin)])
            # po_lines = self.env['purchase.order.line'].search([('order_id', '=', po.id)])
            # for po_line in po_lines:
            #     self.env['purchase.order.line'].received_quantity_computation(po_line.id)
            return pickings_to_validate \
                .with_context(skip_backorder=True, picking_ids_not_to_backorder=self.pick_ids.ids, change_status='moo') \
                .button_validate(from_backorder=True)
        return True


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    sales_count = fields.Float(compute='_compute_sales_count', string='Sold')

    def _compute_sales_count(self):
        r = {}
        self.sales_count = 0
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r
        date_from = fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now() - timedelta(days=365),
                                                                      time.min))

        done_states = self.env['sale.report']._get_done_states()

        domain = [
            ('state', 'in', done_states),
            ('product_id', 'in', self.ids),
            ('date', '>=', date_from),
        ]
        for group in self.env['sale.report'].read_group(domain, ['product_id', 'qty_delivered'], ['product_id']):
            r[group['product_id'][0]] = group['qty_delivered']
        for product in self:
            if not product.id:
                product.sales_count = 0.0
                continue
            product.sales_count = float_round(r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
        return r

    purchased_product_qty = fields.Float(compute='_compute_purchased_product_qty', string='Purchased')

    def _compute_purchased_product_qty(self):
        print("compute purchased product qty")
        date_from = fields.Datetime.to_string(fields.Date.context_today(self) - relativedelta(years=1))
        domain = [
            ('order_id.state', 'in', ['purchase', 'done']),
            ('product_id', 'in', self.ids),
            ('order_id.date_approve', '>=', date_from)
        ]
        order_lines = self.env['purchase.order.line'].read_group(domain, ['product_id', 'qty_received'], ['product_id'])
        purchased_data = dict([(data['product_id'][0], data['qty_received']) for data in order_lines])
        print("purchased_data", purchased_data)
        for product in self:
            if not product.id:
                product.purchased_product_qty = 0.0
                continue
            product.purchased_product_qty = float_round(purchased_data.get(product.id, 0), precision_rounding=product.uom_id.rounding)

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids), ('location_id', '!=', 22)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            date_date_expected_domain_from = [('date', '>=', from_date)]
            domain_move_in += date_date_expected_domain_from
            domain_move_out += date_date_expected_domain_from
        if to_date:
            date_date_expected_domain_to = [('date', '<=', to_date)]
            domain_move_in += date_date_expected_domain_to
            domain_move_out += date_date_expected_domain_to

        Move = self.env['stock.move'].with_context(active_test=False)
        Quant = self.env['stock.quant'].with_context(active_test=False)
        domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = {product.id: product_qty for product, product_qty in Move._read_group(domain_move_in_todo, ['product_id'], ['product_qty:sum'])}
        moves_out_res = {product.id: product_qty for product, product_qty in Move._read_group(domain_move_out_todo, ['product_id'], ['product_qty:sum'])}
        quants_res = {product.id: (quantity, reserved_quantity) for product, quantity, reserved_quantity in Quant._read_group(domain_quant, ['product_id'], ['quantity:sum', 'reserved_quantity:sum'])}
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = {product.id: product_qty for product, product_qty in Move._read_group(domain_move_in_done, ['product_id'], ['product_qty:sum'])}
            moves_out_res_past = {product.id: product_qty for product, product_qty in Move._read_group(domain_move_out_done, ['product_id'], ['product_qty:sum'])}

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            origin_product_id = product._origin.id
            product_id = product.id
            if not origin_product_id:
                res[product_id] = dict.fromkeys(
                    ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available'],
                    0.0,
                )
                continue
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(origin_product_id, [0.0])[0] - moves_in_res_past.get(origin_product_id, 0.0) + moves_out_res_past.get(origin_product_id, 0.0)
            else:
                qty_available = quants_res.get(origin_product_id, [0.0])[0]
            reserved_quantity = quants_res.get(origin_product_id, [False, 0.0])[1]
            res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
            res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(origin_product_id, 0.0), precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(origin_product_id, 0.0), precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)

        return res

# class PurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'
#
#     def received_quantity_computation(self, line_id):
#         po_line = self.env['purchase.order.line'].search([('id', '=', line_id)])
#         stock_moves = self.env['stock.move'].search([('purchase_line_id', '=', po_line.id), ('state', '=', 'done')])
#         print("stock moves", stock_moves)
#         in_qtys_list = [move.product_qty for move in stock_moves if move.location_dest_id.id == 22]
#         print("inqtyslist", in_qtys_list)
#         out_qtys_list = [move.product_qty for move in stock_moves if move.location_dest_id.id == 4]
#         print('outqtyslist', out_qtys_list)
#         in_qtys = sum(in_qtys_list)
#         out_qtys = sum(out_qtys_list)
#         po_line.qty_received = in_qtys - out_qtys


