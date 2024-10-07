from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_round
from collections import defaultdict
from datetime import date, timedelta
from datetime import datetime



class BillReport(models.AbstractModel):
    _name = 'report.manufacter_rck.report_print_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, partners):

        row = 0
        col = 0
        print('data', data['opening'])
        worksheet = workbook.add_worksheet('Report')
        # worksheet.write(1, 1, data['product_id'])
        for open in data['opening']:
            worksheet.write(1, 1, open['name'])
            print('invt qty-----------------', open['qty_available'])
            worksheet.write(2, 2, open['qty_available'])

        # for obj in partners:
        #     worksheet = workbook.add_worksheet('Report')
        #     worksheet.set_column('A:A', 30)
        #     worksheet.set_column('B:B', 40)
        #     worksheet.set_column('C:C', 30)
        #     worksheet.set_column('D:D', 20)
        #     worksheet.set_column('E:E', 20)
        #     worksheet.set_column('F:F', 20)
        #     worksheet.set_column('G:G', 20)
        #     worksheet.set_column('I:I', 25)
        #     worksheet.set_column('J:J', 25)
        #     worksheet.set_column('K:K', 40)
        #     col_format = workbook.add_format({'align': 'left', "align": "center", "border": 1, "bg_color": "#87CEEB"})
        #     worksheet.write(0, 1, 'MATERIAL REQUISITION FORM', col_format)
        #     # col = workbook.add_format({'align': 'left', "align": "center", "border": 1, "bg_color": "#87CEEB"})
        #     col_1 = workbook.add_format({'align': 'center'})
        #     date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd-mm-yyyy','align': 'left'})
        #     row+=1
        #     worksheet.write(row, col , 'WORK NO')
        #     worksheet.write(row, col+1, obj.name)
        #     row+=1
        #     worksheet.write(row, col, 'CUSTOMER NAME')
        #     # vals = self.env['mrp.production'].search([('id', '=', self.cus_name)])
        #     print("Customer Name ----" + str(self))
        #     # print("Mrp Object ----"+ vals)
        #     # for obj in vals:
        #     worksheet.write(row, col+1, obj.cus_name.name or 'None')
        #     row+=1
        #
        #     worksheet.write(row, col, 'PO NO')
        #     worksheet.write(row, col+1, obj.po_num)
        #     row += 1
        #     worksheet.write(row, col, 'DATE')
        #     worksheet.write(row, col+1, obj.po_date, date_style)
        #     row += 1
        #     worksheet.write(row, col, 'PRODUCTED PRODUCT DESCRIPTION')
        #     # worksheet.write(row, col + 1, "[" + obj.product_id.default_code + "]" + obj.product_id.name)
        #     worksheet.write(row, col+2, 'QTY')
        #     worksheet.write(row,  col+3, obj.product_qty)
        #     row += 1
        #
        #
        #
        #     worksheet.write(row, col, 'BILL OF MATERIAL', col_format)
        #     row+=1
        #
        #     row = 8
        #     worksheet.write('A%s' % (row), 'S NO', col_1)
        #     worksheet.write('B%s' % (row), 'DESCRIPTION', col_1)
        #     worksheet.write('C%s' % (row), 'QUANTITY', col_1)
        #     worksheet.write('D%s' % (row), 'STORE ISSUE', col_1)
        #     worksheet.write('E%s' % (row), 'STORE RETURN', col_1)
        #     worksheet.write('F%s' % (row), 'STORE REISSUE/ EXCESS QTY', col_1)
        #     worksheet.write('G%s' % (row), 'END PIECE / SCRAP QTY', col_1)
        #     worksheet.write('I%s' % (row), 'ISSUED BY DATE', col_1)
        #     worksheet.write('J%s' % (row), 'RECEIVED BY DATE', col_1)
        #     worksheet.write('K%s' % (row), 'REMARKS', col_1)
        #     row += 1
        #     # for bom_obj in obj.bom_id:
        #     #     for pro_tem_id in bom_obj.bom_line_ids:
        #     #         print("line Name ----" + str(pro_tem_id.product_id.name))
        #     #         worksheet.write('B%s' % (row), pro_tem_id.product_id.name or 0)
        #     #         worksheet.write('C%s' % (row), pro_tem_id.product_qty or 0)
        #     #         row+=1
        #     #         for rec in obj.move_raw_ids:
        #     #             worksheet.write('D%s' % (row), rec.store_qty or 0)
        #     #             worksheet.write('E%s' % (row), rec.return_qty or 0)
        #     #             row += 1
        #     s_no = 1
        #     raw_row = row
        #     for bom_obj in obj.bom_id:
        #         for pro_tem_id in bom_obj.bom_line_ids:
        #         # for rec in obj.move_raw_ids:
        #             print("line Name ----" + str(pro_tem_id.product_id.name))
        #             worksheet.write('A%s' % (row), s_no, col_1)
        #             worksheet.write('B%s' % (row), pro_tem_id.product_id.name or 0, col_1)
        #             worksheet.write('C%s' % (row), pro_tem_id.product_qty or 0, col_1)
        #             worksheet.write('K%s' % (row), obj.remark or 0, col_1)
        #
        #             row += 1
        #             s_no += 1
        #     for rec in obj.move_raw_ids:
        #             print ("test---"+ str(rec.store_qty))
        #             print("test1---"+ str(rec.return_qty))
        #             worksheet.write('D%s' % (raw_row), rec.store_qty or 0, col_1)
        #             worksheet.write('E%s' % (raw_row), rec.return_qty or 0, col_1)
        #             worksheet.write('I%s' % (raw_row), rec.date ,date_style)
        #             raw_row += 1
        #             s_no += 1
        #     rev = raw_row
        #     total_scrap=0
        #     vals= self.env['stock.scrap'].search([('production_id', '=', obj.id)])
        #     for scr in vals:
        #             print("productionid" + str(scr.scrap_qty))
        #             total_scrap = total_scrap + scr.scrap_qty
        #             print("total scrap" + str(scr.scrap_qty))
        #             worksheet.write('G%s' % (rev), total_scrap or 0, col_1)
        #             rev += 1
        #             s_no += 1
        #
        #     for rec in obj.move_raw_ids:
        #             worksheet.write(21, 0, rec.product_id.qty_available or 0, col_1)
        #
        #
        #
        #     # worksheet.write('G%s' % (row), obj.scrap_qty or 0)
        #
        #     # worksheet.write(row, col, 'S/NO')
        #     #
        #     # worksheet.write(row, col+1, 'DESCRIPTION WITH PARTNUMBER')
        #     # for bom_obj in obj.bom_id:
        #     #     for pro_tem_id in bom_obj.bom_line_ids:
        #     #         print("line Name ----" + str(pro_tem_id.product_id.name))
        #     #         worksheet.write(row, col, pro_tem_id.product_id.name or 0)
        #     #         row+=1
        #     # worksheet.write(row+0, col+3, 'QUANTITY')
        #     # for bom_obj in obj.bom_id:
        #     #     for pro_tem_id in bom_obj.bom_line_ids:
        #     #         print("bom Qty ----" + str(bom_obj.product_qty))
        #     #         print("line Name ----" + str(pro_tem_id.product_qty))
        #     #         worksheet.write(row+1, col, pro_tem_id.product_qty or 0)
