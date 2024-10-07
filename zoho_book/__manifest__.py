{
    'name': 'ZOHO BOOKS Integration',
    'summary': 'Import Contacts,Items,PurchaseOrders From ZOHO BOOKS to Odoo',
    'description': """
                    ZOHO BOOKS Integration , Get Access Token while clicking Button. Import Contacts,Items,PurchaseOrders From ZOHO BOOKS to ODOO
                    """,
    'sequence' : -100,
    'category': 'Extra Tools',
    'author': 'Jagadish-->Jetzerp',
    'depends': [
        'base','contacts', 'stock',"sale","purchase","account",
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/zohobooks.xml',
        'views/view.xml',
        # 'views/assets.xml',
        'views/tree_button.xml',
    ],
    'qweb': [
        'static/src/xml/tree_button.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
