# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import math


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # qos = fields.Char(string='Product UoS Quantity')
    # sch_date = fields.Date(string='Scheduled Date')
    cus_name = fields.Many2one('res.partner', string='Customer Name',
                               states={'draft': [('readonly', False)]})
    cus_code = fields.Char(string='Customer code')
    po_num = fields.Char(string='PO No')
    po_date = fields.Date(string='PO Date')
    pack_details = fields.Char(string='No of Boxes Info')
    no_pack_boxes = fields.Char(string='No of Boxes')
    draw_num = fields.Char(string='Drawing Number')
    revision = fields.Char(string='Revision')
    tes_cert = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Test Certificate')
    ins_term = fields.Char(string='Inspection Terms')
    ins_cert = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Inspection Certificate')
    remark = fields.Char(string='Remarks')
    mrp_scraped_qty = fields.Float("Scrap Qty", compute='get_scrap_qty')

    # colour = fields.Char(string='Colour')
    # quantity = fields.Char(string='Quantity')
    # cycle_time = fields.Char(string='Cycle Time', compute='_compute_cycle_time')

    machine_name = fields.Many2one('machine.machines', string='Machine Name')
    # machine_number = fields.Char(string='Machine Number')
    program_number = fields.Char(string='Program Number')
    order_prepared_by = fields.Many2one('res.users', string='Prepared BY', required=False,
                                        default=lambda self: self.env.user)

    date_planned_start = fields.Datetime(string='Scheduled Date')
    cycle_time = fields.Char(string='Cycle Time', compute='_compute_cycle_time')

    def _compute_cycle_time(self):
        for cyc in self:
            if cyc.state in ('draft', 'confirmed', 'progress', 'to_close') and cyc.product_qty:
                if cyc.product_id.product_tmpl_id.cycle_time:

                    final_result = None
                    seconds = cyc.product_id.product_tmpl_id.cycle_time * cyc.product_qty
                    seconds_in_hour = 60 * 60
                    seconds_in_minute = 60

                    hours = int(seconds // seconds_in_hour)
                    minutes = int((seconds - (hours * seconds_in_hour)) // seconds_in_minute)
                    res_seconds = int((seconds - (hours * seconds_in_hour) - (minutes * seconds_in_minute)))

                    if hours >= 10:
                        final_result = str(hours) + " Hours "
                    else:
                        final_result = "0" + str(hours) + " Hour "

                    if minutes >= 10:
                        final_result += " " + str(minutes) + " Minutes "
                    else:
                        final_result += " 0" + str(minutes) + " Minute "

                    if res_seconds >= 10:
                        final_result += " " + str(res_seconds) + " Seconds"
                    else:
                        final_result += " 0" + str(res_seconds) + " Second"

                    cyc.cycle_time = final_result

                else:
                    cyc.cycle_time = 'None'
            elif cyc.cycle_time:
                cyc.cycle_time = cyc.cycle_time
            else:
                cyc.cycle_time = 'None'

    def get_scrap_qty(self):
        for record in self:
            scrap_id = self.env['stock.scrap'].sudo().search(
                [('production_id', '=', record.id), ('product_id', '=', record.product_id.id)])
            if scrap_id:
                scrap_sum = 0
                for scrap in scrap_id:
                    scrap_sum += scrap.scrap_qty
                record.mrp_scraped_qty = scrap_sum
            else:
                record.mrp_scraped_qty = 0

    @api.onchange('cus_name')
    def choose_bill_of_material_for_the_cus_name_and_product(self):
        boms = self.env['mrp.bom'].search([])
        print("self.product_id.id", self.product_id.id)
        filtered_bom = boms.filtered(lambda p: p.product_tmpl_id.id == self.product_id.id and p.cus_name == self.cus_name)
        print(".........filtered_bom", filtered_bom)
        if len(filtered_bom) == 1:
            self.bom_id = filtered_bom.id

    # @api.onchange('cus_name')
    # def set_bom_id_for_customer(self):
    #     if self.cus_name:
    #         return {"domain": {"bom_id": [
    #             '&',
    #             '|',
    #             ('company_id', '=', False),
    #             ('company_id', '=', self.company_id.id),
    #             '&',
    #             '|',
    #             ('product_id', '=', self.product_id.id),
    #             '&',
    #             ('product_tmpl_id.product_variant_ids', '=', self.product_id.id),
    #             ('product_id', '=', False),
    #             ('type', '=', 'normal'), ('cus_name', '=', self.cus_name.id)]}}
    #
    #     else:
    #         return {"domain": {"bom_id": [
    #             '&',
    #             '|',
    #             ('company_id', '=', False),
    #             ('company_id', '=', self.company_id.id),
    #             '&',
    #             '|',
    #             ('product_id', '=', self.product_id.id),
    #             '&',
    #             ('product_tmpl_id.product_variant_ids', '=', self.product_id.id),
    #             ('product_id', '=', False),
    #             ('type', '=', 'normal')]}}

    # @api.onchange('cus_name')
    # def set_customer_boq_id(self):
    #     if self.cus_name:
    #         cus_id = self.cus_name.id or False
    #         print("11111111111111111111111111")
    #         bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id,
    #                                             company_id=self.company_id.id, bom_type='normal', customer_id=cus_id)
    #         if bom:
    #             self.bom_id = bom.id
    #             self.product_qty = self.bom_id.product_qty
    #             self.product_uom_id = self.bom_id.product_uom_id.id
    #         else:
    #             self.bom_id = False
    #             self.product_uom_id = self.product_id.uom_id.id
    #     else:
    #         self.bom_id = False
    #         self.product_uom_id = self.product_id.uom_id.id

    # @api.onchange('product_id', 'picking_type_id', 'company_id')
    # def onchange_product_id(self):
    #     """ Finds UoM of changed product. """
    #     if not self.product_id:
    #         self.bom_id = False
    #     elif not self.bom_id or self.bom_id.product_tmpl_id != self.product_tmpl_id or (
    #             self.bom_id.product_id and self.bom_id.product_id != self.product_id):
    #         cus_id = self.cus_name.id or False
    #         print("22222222222222222")
    #         bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id,
    #                                             company_id=self.company_id.id, bom_type='normal', customer_id=cus_id)
    #         if bom:
    #             self.bom_id = bom.id
    #             self.product_qty = self.bom_id.product_qty
    #             self.product_uom_id = self.bom_id.product_uom_id.id
    #         else:
    #             self.bom_id = False
    #             self.product_uom_id = self.product_id.uom_id.id

    # def button_mark_done(self):
    #     for record in self:
    #         # record.button_unreserve()
    #         for order in record.move_raw_ids:
    #             if not order.product_id.qty_available >= order.product_uom_qty:
    #                 raise ValidationError(_("Raw Material's Not Available."))
    #
    #     return super(MrpProduction, self).button_mark_done()
    #



class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    cus_name = fields.Many2one('res.partner', string='Customer Name')

    # @api.model
    # def _bom_find(self, product_tmpl=None, product=None, picking_type=None, company_id=False, bom_type=False,
    #               customer_id=False):
    #     """ Finds BoM for particular product, picking and company """
    #     if product and product.type == 'service' or product_tmpl and product_tmpl.type == 'service':
    #         return self.env['mrp.bom']
    #     print("44444444444444444444444444")
    #     domain = self._bom_find_domain(products=product, picking_type=picking_type,
    #                                    company_id=company_id, bom_type=bom_type)
    #     if domain is False:
    #         return self.env['mrp.bom']
    #
    #     # add customer search in BOM
    #     if customer_id:
    #         domain += [('cus_name', '=', customer_id)]
    #
    #     return self.search(domain, order='sequence, product_id', limit=1)



    # @api.multi
    # def action_assign(self):
    #     res = super(manufacter_rck, self).action_assign()
    #     for record in self:
    #         for order in record.move_raw_ids:
    #             quantity_search = self.env['stock.quant'].search(
    #                 [('product_id', '=', order.product_id.id), ('location_id.usage', '=', 'internal')])
    #             if quantity_search:
    #                 order.available_qty = quantity_search.mapped('quantity')[0]
    #     return res
    #
    # @api.model
    # def create(self, values):
    #     res = super(manufacter_rck, self).create(values)
    #     for record in res:
    #         for order in record.move_raw_ids:
    #             quantity_search = self.env['stock.quant'].search(
    #                 [('product_id', '=', order.product_id.id), ('location_id.usage', '=', 'internal')])
    #             if quantity_search:
    #                 order.available_qty = quantity_search.mapped('quantity')[0]
    #     return res
    #
    # @api.multi
    # def write(self, vals):
    #     res = super(manufacter_rck, self).write(vals)
    #     for record in self:
    #         for order in record.move_raw_ids:
    #             quantity_search = self.env['stock.quant'].search(
    #                 [('product_id', '=', order.product_id.id), ('location_id.usage', '=', 'internal')])
    #             if quantity_search:
    #                 order.available_qty = quantity_search.mapped('quantity')[0]
    #     return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    available_qty = fields.Float("Available Qty", compute='get_available_qty', store=True)

    #
    #     @api.onchange('product_id')
    #     def onchange_prod_id(self):
    #         for record in self:
    #             quantity_search = self.env['stock.quant'].search(
    #                 [('product_id', '=', record.product_id.id), ('location_id.usage', '=', 'internal')])
    #             if quantity_search:
    #                 quantity = quantity_search.mapped('quantity')[0] - quantity_search.mapped('reserved_quantity')[0]
    #                 record.available_qty = quantity if quantity > 0 else 0

    @api.depends('product_id')
    def get_available_qty(self):
        for record in self:
            quantity_search = self.env['stock.quant'].search(
                [('product_id', '=', record.product_id.id), ('location_id.usage', '=', 'internal')])
            if quantity_search:
                quantity = quantity_search.mapped('quantity')[0] - quantity_search.mapped('reserved_quantity')[0]
                record.available_qty = quantity if quantity > 0 else 0
            else:
                record.available_qty = 0


# class MrpBom(models.Model):
#     _inherit = 'mrp.bom'
#
#     # code commented by britto freelancer to stop the quick book dependency
#     # product_tmpl_id = fields.Many2one(
#     #     'product.template', 'Product',
#     #     domain="[('type', 'in', ['product', 'consu']),('qbo_product_id','!=',None)]", required=True)
#
#     product_tmpl_id = fields.Many2one(
#         'product.template', 'Product',
#         domain="[('type', 'in', ['product', 'consu'])]", required=True)




