from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class apex_machine(models.Model):
    _name = 'machine.machines'

    name = fields.Char("Machine Name")


# class Valuation(models.Model):
#     _inherit = 'stock.valuation.layer'
#
#     create_date = fields.Datetime(compute='compute_create_date', readonly=True)
#
#     def compute_create_date(self):
#         for rec in self:
#             for rev in rec.stock_move_id:
#                 if rev.purchase_line_id:
#                     rec.create_date = rev.purchase_line_id.date_planned
#                     rev.date = rev.purchase_line_id.date_planned
#                     # date = datetime.datetime.now()
#                     # print(date)
#                 else:
#                     if rev:
#                         search = self.env['stock.move'].search([
#                             ('date', '=', rev.date)
#                         ])
#                         for line in search:
#                             rec.create_date = line.date
#
#             if not rec.stock_move_id:
#                 rec.create_date = rec.write_date
