from odoo import models, fields, api, _
from odoo import api, models, _
from datetime import date, timedelta
from datetime import datetime

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object


class SalesStatusXlsx(models.AbstractModel):
    _name = 'report.rck_sale_order_report.status_rpt'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet()
        header_main = workbook.add_format({
            'bold': 2,
            'border': 2,
            'align': 'center',
            'fg_color': '1b75bc',
            'color': 'white',
        })
        header = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'fg_color': '1b75bc',
            'color': 'white',
        })
        sheet.set_row(1, 60)
        heading = "Sales Status Report \n\n Report Period :  " + data['start_date'] + "  TO  " + data['end_date'] + "\n"

        sheet.merge_range('A2:I2', heading, header_main)

        border = workbook.add_format({'border': 1, 'align': 'center'})
        row = 3
        col = 0

        sheet.set_column('B:B', 16)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 18)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 38)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)

        sheet.write(row, col, 'S.No', header)
        col += 1
        sheet.write(row, col, 'Order Number', header)
        col += 1
        sheet.write(row, col, 'Order Date', header)
        col += 1
        sheet.write(row, col, 'Customer Name', header)
        col += 1
        sheet.write(row, col, 'Part Number', header)
        col += 1
        sheet.write(row, col, 'Description', header)
        col += 1
        sheet.write(row, col, 'Total Qty', header)
        col += 1
        sheet.write(row, col, 'Dispatched Qty', header)
        col += 1
        sheet.write(row, col, 'Balance Qty', header)

        row += 1
        col = 0
        i = 1

        sale_orders = data['sale_orders']
        for order in sale_orders:
            sheet.write(row, col, i, border)
            col += 1
            sheet.write(row, col, order['order_number'], border)
            col += 1
            sheet.write(row, col, order['order_date'], border)
            col += 1
            sheet.write(row, col, order['consumer_id'], border)
            col += 1
            sheet.write(row, col, order['part_number'], border)
            col += 1
            sheet.write(row, col, order['product_name'], border)
            col += 1
            sheet.write(row, col, order['total_qty'], border)
            col += 1
            sheet.write(row, col, order['delivered_qty'], border)
            col += 1
            sheet.write(row, col, order['balance_qty'], border)
            i += 1
            col = 0
            row += 1