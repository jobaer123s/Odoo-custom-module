{
    'name': 'Statement SMS to Customer',
    'author': 'Ogroni Informatix Limited',
    'version': '1.0.0',
    'summary': 'Statement SMS to Customer for Odoo v13',
    'description': 'Statement SMS to Customer',
    'sequence': 15,
    'category': 'SMS',
    'website': 'https://ogroni.com/',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'depends': ['base', 'base_setup', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/view_statement_sms_to_customer.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}