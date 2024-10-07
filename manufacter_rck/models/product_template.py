from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    drawing_number = fields.Char(string='Drawing Number')
    revision = fields.Char(string='Revision')
    program_number = fields.Char(string='Program Number')
    cycle_time = fields.Integer(string='Cycle Time (in secs)')

