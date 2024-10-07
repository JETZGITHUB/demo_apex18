{
    'name': 'new updates',
    'sequence': -10,
    'summary': 'Removing tax for Sale and Purchase, inventory adjustment serial number auto generator',
    'description': """  This module helps to Removing tax for Sale and Purchase,
                        Inventory adjustment reference Number auto generating,
                        if store quantity greater than on hand Quantity will rise validation error. 
                        """,
    'license': 'LGPL-3',
    'category': 'Stock',
    'author': 'Jagadish-->JETZERP',
    'website': '',
    'images': [],
    "depends": [
        "mrp", "sale",
        "sale_stock",
        "purchase",'stock', 'account', "mrp",
    ],
    'data': [
        # 'data/data.xml',
        'views/remove_tax_in_sale.xml',
    ],
    # 'images': [
    #     'static/description//home/icon.png',
    # ],
    # 'pre_init_hook':'pre_init_check',
    'installable': True,
    'application': True,
    'auto_install': False,
}