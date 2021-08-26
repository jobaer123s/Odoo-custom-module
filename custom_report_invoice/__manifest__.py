{
    'name': 'Custom Report Invoice',
    'author': 'Ogroni Informatix Limited',
    'version': '1.0.0',
    'summary': 'Custom Report Invoice for Odoo v13',
    'sequence': 15,
    'category': 'Report',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'website': 'https://ogroni.com/',
    'depends': ['base', 'base_setup', 'account', 'base_accounting_kit', 'hr_payroll_community'],
    'data': [
        # 'security/ir.model.access.csv',
        'report/report_invoice_inherit.xml',
        'report/custom_report_statement.xml',
        'report/custom_report_statement_tmpl.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
