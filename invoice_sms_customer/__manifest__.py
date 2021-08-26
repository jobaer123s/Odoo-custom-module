{
    'name': 'Invoice SMS to Customer',
    'author': 'Ogroni Informatix Limited',
    'version': '1.0.0',
    'summary': 'Invoice SMS to Customer for Odoo v13',
    'description': 'Invoice SMS to Customer',
    'sequence': 15,
    'category': 'SMS',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'website': 'https://www.ogroni.com',
    'depends': ['base', 'base_setup', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/view_invoice_sms_to_customer.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}