{
    'name': "Custom Customer Reference",
    'author': "Ogroni Informatix Limited",
    'version': '13.1.0.0',
    'category': "Sale",
    'summary': "Custom Customer Reference Module for Odoo v13",
    'sequence': '11',
    'description': """
    Custom Customer Reference Module for Odoo v13
    """,
    'website': 'https://ogroni.net/',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_reference.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}