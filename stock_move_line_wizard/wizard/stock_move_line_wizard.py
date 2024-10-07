from odoo import api, models, fields, _
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import format_date


class StockMoveLineWizard(models.TransientModel):
    _name = 'stock.move.line.wizard'

    stock_line_ids = fields.Many2many('stock.move.line', string="Stock Lines")
    picking = fields.Many2one('stock.picking')


    @api.model
    def default_get(self, fields):
        res = super(StockMoveLineWizard, self).default_get(fields)
        active_picking_id = self.env.context.get('active_id')
        res['picking'] = active_picking_id
        print(active_picking_id)
        if active_picking_id:
            pick = self.env['stock.picking'].browse(active_picking_id)
            searchs = self.env['stock.move.line'].search([('picking_id', '=', pick.id), ('qty_done', '!=', 0)])
            
            # Loop over the move lines, not move
            for move_line in pick.move_line_ids:
                val = {'uom_line_value': move_line.uom_line_value}
                move_line.write(val)
            
            # Set stock_line_ids with the result of the search
            stock_line_ids = [(6, 0, [move.id for move in searchs])]
            res['stock_line_ids'] = stock_line_ids
        return res

    # @api.model
    # def default_get(self, fields):
    #     res = super(StockMoveLineWizard, self).default_get(fields)
    #     active_picking_id = self.env.context.get('active_id')
    #     res['picking'] = active_picking_id
    #     print(active_picking_id)
    #     if active_picking_id:
    #         pick = self.env['stock.picking'].browse(active_picking_id)
    #         searchs = self.env['stock.move.line'].search([('reference', '=', pick.name), ('qty_done', '!=', 0),
    #                                                       ])
    #         for product_line in pick.move_ids_without_package:
    #             search = self.env['stock.move.line'].search([('reference', '=', pick.name), ('qty_done', '!=', 0),
    #                                                          ('product_id', '=', product_line.product_id.id)])
    #             # print(pick.name, pick.move_ids_without_package.uom_line_value)
    #             # for pick_line in pick.move_ids_without_package:
    #             val = {'uom_line_value': product_line.uom_line_value}
    #             search.write(val)
    #         stock_line_ids = [(6, 0, [move.id for move in searchs])]
    #         res['stock_line_ids'] = stock_line_ids
    #     return res

    def validate(self):
        print("validate aaga kadaisila, stock_line_ids", self.read(0))
        picking_id = self.env['stock.picking'].search([('id', '=', self.picking.id)])
        print("picking_id env context", picking_id.env.context)
        print("self. active_id", self.env.context)
        ctx = dict(picking_id.env.context)  # active_id = purchase_order.id
        ctx.pop('default_immediate_transfer', None)
        self = picking_id.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in picking_id:  # stock_picking.id
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([picking_id.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(
                float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(
                float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line
                in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:  # stock_move_line.id
                    product = line.product_id  # product_id.id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(
                    products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(
                    pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _(
                    '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(
                    pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
                    ', '.join(pickings_without_lots.mapped('name')),
                    ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())
        origin = self.env['stock.picking'].search([('id', '=', ctx['active_id'])]).origin
        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=picking_id.ids)  # stock_picking.id
        res = self._pre_action_done_hook()
        if res is not True:
            print("the court is adjunt")
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            print("context picking ids not to backorder")
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            print("context to backorder")
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
        print("print the context", self.env.context)
        self.env['purchase.order'].change_status(origin)
        return True


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def call_wizard(self):
        return {
            'name': _("Confirmation "),
            'res_model': 'stock.move.line.wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('stock_move_line_wizard.stock_move_line_wizard_form').id,
            'target': 'new'
        }


class StockMoveLines(models.Model):
    _inherit = "stock.move.line"

    uom_line_value = fields.Float(string="Conversion")
    qty_done = fields.Float(default=0.0, digits=(12, 6), copy=False)


class StockBackorderConfirmation(models.TransientModel):
    _inherit = "stock.backorder.confirmation"

    def process(self):
        print("process process process")
        pickings_to_do = self.env['stock.picking']
        pickings_not_to_do = self.env['stock.picking']
        for line in self.backorder_confirmation_line_ids:
            if line.to_backorder is True:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id

        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            print("process if 1")
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate).with_context(
                skip_backorder=True)
            ctx = self.env.context
            origin = self.env['stock.picking'].search([('id', '=', ctx['active_id'])]).origin
            self.env['purchase.order'].change_status(origin, True)
            if pickings_not_to_do:
                print("process if 2")
                self._check_less_quantities_than_expected(pickings_not_to_do)
                pickings_to_validate = pickings_to_validate.with_context(
                    picking_ids_not_to_backorder=pickings_not_to_do.ids)
            return pickings_to_validate.button_validate()
        return True

    def process_cancel_backorder(self):
        print('process cancel backorder')
        pickings_to_validate_ids = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate_ids:
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate_ids)
            self._check_less_quantities_than_expected(pickings_to_validate)
            ctx = self.env.context
            origin = self.env['stock.picking'].search([('id', '=', ctx['active_id'])]).origin
            self.env['purchase.order'].change_status(origin)
            return pickings_to_validate \
                .with_context(skip_backorder=True, picking_ids_not_to_backorder=self.pick_ids.ids, change_status='moo') \
                .button_validate()
        return True


