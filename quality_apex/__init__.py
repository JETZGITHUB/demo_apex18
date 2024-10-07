from . import models
# def edit_operation_receipts(cr):
#     print(f"location_qualities id::{cr.ref('location_quality')}")
#     cr.execute(f"update stock_picking_type set default_location_dest_id={cr.ref('location_quality').id} where id = {1}")

# from odoo import api, SUPERUSER_ID
# def edit_operation_receipts(cr, registry):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     operation_receipt = env['stock.picking.type'].search([('id', '=', 1)])
#     operation_receipt.write({
#           'default_location_dest_id': env.ref('quality.location_quality').id
#     })
#


def edit_operation_receipts(env):
    # env = api.Environment(cr, SUPERUSER_ID, {})
    operation_receipt = env['stock.picking.type'].search([('id', '=', 1)])
    operation_receipt.write({
          'default_location_dest_id': env.ref('quality_apex.location_quality').id
    })