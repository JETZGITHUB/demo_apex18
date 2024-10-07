{
    'name': "Quality Control",
    'author': "Kumar",
    'category': "Extra-Tools",
    'application': True,
    'depends': ['base', 'stock', 'zoho_book', 'purchase'],
    'data': ['security/user_groups.xml',
             'data/initial_records.xml',
             'security/ir.model.access.csv',
             'views/quality_views.xml',
             'views/view.xml'],
    'post_init_hook': 'edit_operation_receipts',
    'sequence': -2000
}
