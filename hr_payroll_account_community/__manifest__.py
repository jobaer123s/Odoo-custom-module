# -*- coding: utf-8 -*-

{
    'name': 'Odoo13 Payroll Accounting',
    'category': 'Generic Modules/Human Resources',
    'summary': """
          Generic Payroll system Integrated with Accounting,Expense Encoding,Payment Encoding,Company Contribution Management
    """,
    'description': """Odoo13 Payroll Accounting,Odoo13 Payroll,Odoo 13,Payroll Accounting,Accounting""",
    'version': '13.0.1.0.1',
    'author': 'Ogroni Informatix Limited',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'website': 'https://www.ogroni.com',
    'depends': ['hr_payroll_community', 'account'],
    'images': ['static/description/banner.gif'],
    'data': ['views/hr_payroll_account_views.xml'],
    'test': ['../account/test/account_minimal_test.xml'],
    'license': 'AGPL-3',
}
