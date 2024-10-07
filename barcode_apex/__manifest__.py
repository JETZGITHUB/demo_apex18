{
    "name": "Apex Barcodes",
    "Author": "Athreya",
    "application": True,
    "depends": ['base', 'product'],
    "data": ['security/ir.model.access.csv',
        'views/scan_data_view.xml',
             'views/overview.xml',
             'views/view.xml',
             'views/barcode.xml',
             'views/difference_view.xml',
             # 'views/assets.xml'
             ],
    "css": 'views/difference_tree_column.css',
    # "qweb": ['static/src/xml/kanban_button.xml'],
    'sequence': -2001
}