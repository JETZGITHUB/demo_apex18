{
    'name': 'Stock Move Line Wizard',
    'summary': 'Stock Move Line Wizard',
    'description': 'Stock Move Line Wizard',
    'sequence' : -1000,
    'category': 'Extra Tools',
    'depends': [
        'base','account', 'contacts', 'stock', "sale", "purchase", "account", "l10n_in",
        ],
    'data':['views/stock_move_line_wizard.xml',
            'security/ir.model.access.csv'],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': True,
}