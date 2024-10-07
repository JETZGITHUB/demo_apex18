from odoo import api, fields, models, tools, SUPERUSER_ID, _,modules
from odoo.exceptions import ValidationError
from datetime import datetime
import time

class SalesStatus(models.TransientModel):
    _name = "sales_status.report"

    customer_id = fields.Many2one('res.partner',string='Customer Name')
    from_date = fields.Date('From Date',required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    to_date = fields.Date('To Date',required=True,default=lambda *a: time.strftime('%Y-%m-%d'))

    def date_check(self):
        if self.from_date > self.to_date:
            raise ValidationError(_('From date should not be greater than to date'))

    def get_sale_objects(self):
        from_date = datetime.combine(self.from_date, datetime.min.time())
        to_date = datetime.combine(self.to_date, datetime.max.time())
        domain_val = [('state','not in',('draft','cancel')),('date_order','>=',from_date),('date_order','<=',to_date)]
        if self.customer_id:
            domain_val = [('partner_id','=',self.customer_id.id),('state', 'not in', ('draft', 'cancel')), ('date_order', '>=', from_date), ('date_order', '<=', to_date)]
        sale_orders = self.env['sale.order'].search(domain_val)

        order_vals = []
        for order in sale_orders:
            for line in order.order_line:
                blance_qty = line.product_uom_qty - line.qty_delivered
                if blance_qty > 0:
                    order_vals.append({
                        'order_number':order.name,
                        'order_date':order.date_order.date(),
                        'consumer_id':order.partner_id.name,
                        'part_number':line.product_id.default_code or '',
                        'product_name':line.product_id.name,
                        'total_qty':line.product_uom_qty,
                        'delivered_qty':line.qty_delivered,
                        'balance_qty': line.product_uom_qty - line.qty_delivered,
                    })

        if not order_vals:
            raise ValidationError(_('No Data found to generate Sales Status Report'))

        return order_vals

    def xls_status_report(self):
        self.date_check()
        data = {'start_date': self.from_date,
                'end_date': self.to_date,
                'sale_orders': self.get_sale_objects(),
                'customer_id':self.customer_id
                }
        return self.env.ref('rck_sale_order_report.rck_status_rpt').report_action(None, data=data)