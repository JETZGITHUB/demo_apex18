from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class OwnConsumption(models.TransientModel):
    _name = 'own.consumption.wizard'

    @api.model
    def default_get(self, vals):
        res = super(OwnConsumption, self).default_get(vals)
        res['product_id'] = self.env.context.get('active_id')
        return res

    product_id = fields.Many2one('product.template', readonly=True)
    quantity = fields.Float('Quantity')
    onhand_qty = fields.Float(related='product_id.qty_available')
    uom_id = fields.Many2one(related='product_id.uom_id')
    location_id = fields.Many2one("stock.location", string="From", default=8, readonly=True)
    location_dest_id = fields.Many2one("stock.location", string="To", default=19, readonly=True)
    use_for = fields.Text("Used For", required=True)

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.quantity > self.onhand_qty:
            raise ValidationError(_("NOT ENOUGH QUANTITIES IN STOCK"))

    def confirm(self):
        print("own_consumption--models--confirm()--self.product_id.id", self.product_id.id)
        transfer = self.env['stock.picking']
        operation_type = self.env['stock.picking.type'].search([('name', '=', 'operation own consumption')])
        print("operation type.id", operation_type.id)
        item = {
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'picking_type_id': operation_type.id,
            'location_id': operation_type.default_location_src_id.id,
            'location_dest_id': operation_type.default_location_dest_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_id.uom_id.id
        }
        vals = {
            'partner_id': self.env.user.partner_id.id,
            'picking_type_id': operation_type.id,
            'location_id': operation_type.default_location_src_id.id,
            'location_dest_id': operation_type.default_location_dest_id.id,
            'move_ids_without_package': [(0, 0, item)],
            'note': self.use_for
        }
        draft_pick = transfer.create(vals)
        draft_pick.action_confirm()
        draft_pick.action_assign()
        for line in draft_pick.move_line_ids_without_package:
            line.quantity = self.quantity
        draft_pick.button_validate()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_own_consumption_wizard(self):
        print("hey beetha bali habi balubathi bali habi balley balley balihabi")
        return {
            'name': _("Own Consumption"),
            'res_model': 'own.consumption.wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('own_consumption.view_own_consumption_wizard_form').id,
            'target': 'new'
        }
