from odoo import models, fields, api, _

import pandas
import re

df_xl = pandas.read_excel('/home/jetz/Documents/kg_to_m.xlsx')


class zohoBooks(models.Model):
    _inherit = 'zoho.books'

    def show_unit_of_measure(self):
        for row_ser in df_xl.iterrows():
            print(".........row_serof 1", row_ser[1].to_dict())
            row_dict = row_ser[1].to_dict()
            product = self.env['product.template'].search([('default_code', '=', row_dict['PART NUMBER'])])
            # print("UNIT---->", product.default_code)
            for prod in product:
                if prod.uom_id.name != 'in':
                    print("..........defautl_code", prod.default_code)
                    print("............UNIT", prod.uom_id.name)
                else:
                    unit_name = f"KG_{prod.default_code}"
                    vals = {
                        'name': unit_name,
                        'category_id': 4,
                        'factor': row_dict['conver'],
                        'active': True,
                        'uom_type': 'smaller'
                    }
                    new_unit = self.env['uom.uom'].create(vals)
                    print("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm", new_unit.id)
                    prod.uom_po_id = new_unit
                    print("rin thin thin thin t=")

    def correct_actual_qty(self):
        print("jalabula junguh dama duma dunguh")
        pos_not_done = self.env['purchase.order'].search([('state', 'in', ['purchase', 'partial', 'complete_receive'])])
        for po in pos_not_done:
            po_lines = self.env['purchase.order.line'].search([('order_id', '=', po.id)])
            for po_line in po_lines:
                print("ding dong", po_line.ordered_qty)
                if po_line.ordered_qty:
                    print(f"kg irukkaley: {'KG' in po_line.product_id.uom_po_id.name}")
                    if 'KG' in po_line.product_id.uom_po_id.name:
                        formatted_order_qty = re.sub('[^0-9.]', " ", po_line.ordered_qty)
                        print("..........", formatted_order_qty)
                        print(".....pandasuuma.....", po_line.product_id.uom_po_id, "nayagam meendum", po_line.product_uom)

                        po_line.product_uom = po_line.product_id.uom_po_id.id
                        stock_moves = self.env['stock.move'].search([('purchase_line_id', '=', po_line.id)])
                        for stock_move in stock_moves:
                                print(".....factor", stock_move.product_id.uom_po_id.factor)
                                conversion_ratio = stock_move.product_id.uom_po_id.factor
                                num_formatted_order_qty = float(formatted_order_qty)
                                print(".ordered quty", num_formatted_order_qty)
                                no_of_metres = num_formatted_order_qty/conversion_ratio
                                print("no of metres", no_of_metres)
                                inch_qty = no_of_metres * 39.37
                                print("inch qty??????????????????/", inch_qty)
                                stock_move.product_uom_qty = inch_qty

                        po_line.product_qty = float(formatted_order_qty)