{
    'name' : 'Product Reserved Stock Information',
    'version' : '1.0',
    'summary': 'Product Reserved Stock Information',
    'sequence': 1,
    'description': "",
    'category': 'Extra Tool',
    'author': '',
    'website': '',
    'depends':['base','web','stock'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/product_reserved_stock.xml",
        "report/report_stock_reserved.xml",
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}