{
    'name': 'Custom SMS Gateway',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'SMS Gateway Configuration for Odoo v13',
    'description': """This module helps to configure custom SMS gateway for Odoo v13""",
    'author': 'Ogroni Informatix Limited',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'website': 'https://ogroni.net/',
    'depends': ['sms'],
    'data': [
        'views/sms_mail_server.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
