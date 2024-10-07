{
    'name': "manufacter_rck",
    'summary': """  """,
    'description': """  """,
    'author': "Rck Techiees",
    'website': "http://www.rcktechiees.com",
    'category': 'Manufacturing Order',
    'version': '0.1',
    'depends': ['base','mrp', 'zoho_book'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'reports/manufacturer_report.xml',
        'reports/internal_header_template.xml',
        'reports/print_report.xml',
        'views/remove_manage_database.xml',
        'views/stock_total_value.xml',
        'views/product_template.xml'
    ],
}
