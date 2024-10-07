# code commented by jagadishmagesh1999@gmail.com

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                # amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                # 'amount_tax': currency.round(amount_tax),
                'amount_total': amount_untaxed,
                                # + amount_tax,
            })

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                # 'amount_tax': amount_tax,
                'amount_total': amount_untaxed,
                                # + amount_tax,
            })

#
# class Inventory(models.Model):
#     _inherit = "stock.inventory"
#
#     name = fields.Char(
#         'Inventory Reference', default=lambda self: _('Inventory'),
#         readonly=True, required=True,
#         states={'draft': [('readonly', False), ]})
#
#     @api.model
#     def create(self, vals):
#         if vals.get('name', _('Inventory')) == _('Inventory'):
#             vals['name'] = self.env['ir.sequence'].next_by_code('stock.inventory') or _('Inventory')
#         res = super(Inventory, self).create(vals)
#         return res


# class MroProduction(models.Model):
#     _inherit = 'mrp.production'
#
#     def write(self, vals):
#         res = super(MroProduction, self).write(vals)
#         if self.state != 'done':
#             for line in self.move_raw_ids:
#                 current_stock = self.env['stock.quant'].search(
#                     [('product_id', '=', line.product_id.id), ('location_id', '=', 8)])
#
#                 if current_stock:
#                     if line.store_qty > current_stock.quantity:
#                         raise ValidationError(
#                             'Please check Your stock, product {} have only {} quantity !'.format(
#                                 line.product_id.name, current_stock.quantity))
#             return res

    # def write(self, vals):
    #     res = super(MroProduction, self).write(vals)
    #     if self.state != 'done':
    #         for line in self.move_raw_ids:
    #             current_stock = self.env['stock.quant'].search(
    #                 [('product_id', '=', line.product_id.id), ('location_id', '=', 8)])
    #
    #             if current_stock:
    #                 for rec in line.product_id:
    #                     for res in self.bom_id:
    #                         for rev in res.bom_line_ids:
    #                             if rec.uom_id.name == rev.product_uom_id.name:
    #                                 if line.store_qty > current_stock.quantity:
    #                                     raise ValidationError(
    #                                         ' Please check Your stock, product {} have only {} quantity !'.format(
    #                                             line.product_id.name, current_stock.quantity))
    #         return res