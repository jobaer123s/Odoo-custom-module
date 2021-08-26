{
    'name': "Custom Sales Report",
    'version': '1.0.0',
    'category': 'Report',
    'sequence': '2',
    'summary': 'Custom Sales Report for Odoo v13',
    'description': """
Custom Sales Report for Odoo v13
    """,
    'author': "Ogroni Informatix Limited",
    'company': "Ogroni Informatix Limited",
    'maintainer': "Ogroni Informatix Limited",
    'website': "https://ogroni.net/",
    'depends': ['account', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'report/custom_sales_report.xml',
        'report/custom_sales_report_pdf_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}