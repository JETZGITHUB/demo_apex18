{
    'name': 'INVENTORY REPORT',
    'summary': 'TO PRINT THE EXCEL REPORT OF YOUR INVENTORY',
    'description': """
                    $TO PRINT THE FOLLOWING:-
                      *INVENTORY VALUATION REPORT,
                      *INVENTORY MOVEMENT REPORT,
                    $AND ALSO TO VIEW INVENTORY VALUATION IN THE UI
                    """,
    'sequence' : -100,
    'category': 'Extra Tools',
    'author': 'Hukum',
    'depends': [
        'base', 'contacts', 'stock', "sale", "purchase", "account"
        ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/inventory_report_wizard.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}