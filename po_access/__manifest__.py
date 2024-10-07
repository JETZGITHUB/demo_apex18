{
    'name': 'PO Access',
    'summary': 'PO Access',
    'description': ' PO Access Based On User Role ',
    'sequence' : -888,
    'category': 'Purchase',
    'author': 'Jagadish And Monish -- Jetzerp',
    'depends': [
        'base', 'contacts', 'stock', "sale", "zoho_book", "purchase", "account", "l10n_in",
        ],
    'data': ['views/hide.xml',
             'security/ir.model.access.csv'],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': True,
}