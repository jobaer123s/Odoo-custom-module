{
    'name': 'Custom Report Ledger',
    'author': 'Ogroni Informatix Limited',
    'version': '1.0.0',
    'summary': 'Custom Report Ledger for Odoo v13',
    'sequence': 15,
    'description': """ Custom Report Ledger """,
    'category': 'Report',
    'website': 'https://ogroni.com/',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'depends': ['base_setup', 'base', 'account', 'base_accounting_kit'],
    'data': [
        'security/ir.model.access.csv',
        'report/detail_customer_ledger.xml',
        'report/detail_customer_ledger_pdf_templates.xml',
        'report/summarized_customer_ledger.xml',
        'report/summarized_customer_ledger_pdf_templates.xml',
        'report/customer_ledger.xml',
        'report/customer_ledger_pdf_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

