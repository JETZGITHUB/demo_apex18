from odoo import api, models

class ReservedStockReport(models.AbstractModel):
    _name = 'report.product_reserved_stock_info.prd_stock_res'
    _description = "Stock Reservation Report"

    @api.model
    def _get_report_values(self, docids, data=None):

        ForecastedReport = self.env['report.stock.report_product_product_replenishment']._get_report_data(product_variant_ids=docids)

        line_vals = []
        reserved_total = 0
        for line_data in ForecastedReport['lines']:
            if line_data['reservation']:
                line_vals.append(line_data)
                reserved_total += line_data['quantity']

        ForecastedReport['lines'] = line_vals
        ForecastedReport['reserved_total'] = reserved_total

        return {
            'data': data,
            'doc_ids': docids,
            'doc_model': 'product.product',
            'docs': ForecastedReport,
        }