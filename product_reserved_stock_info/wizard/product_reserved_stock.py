from odoo import api, fields, models, _, tools
from odoo.http import request

class ProductReseredStockDetails(models.TransientModel):

    _name = 'product.reserved_stock_details'
    _description = "Product Reserved Stock Details"

    product_id = fields.Many2one(comodel_name='product.product', string='Product Id')

    def submit_product(self):
        action = self.env["ir.actions.actions"]._for_xml_id("product_reserved_stock_info.stock_reserved_prd_report")
        action['context'] = {'default_product_id': self.product_id.id, 'active_model': 'product.product', 'active_id': self.product_id.id, 'active_ids': [self.product_id.id]}
        return action