# -*- coding: utf-8 -*-

{
    'name': 'Odoo13 Employee Contracts Types',
    'version': '13.0.1.1.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """ Contract type in contracts for Odoo v13""",
    'description': """Odoo13 Employee Contracts Types,Odoo13 Employee, Employee Contracts, Odoo 13""",
    'author': 'Ogroni Informatix Limited',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'website': 'https://ogroni.com/',
    'depends': ['hr','hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'data/hr_contract_type_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}