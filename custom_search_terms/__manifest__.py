# -*- coding: utf-8 -*-
{
    'name': 'Custom Search Terms',
    'version': '1.0.0',
    'category': 'Custom Search Terms',
    'sequence': 20,
    'summary': 'Custom Search Terms for Odoo v13',
    'description': """Custom Search Terms""",
    'author': 'Ogroni Informatix Limited',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'website': 'https://ogroni.net/',
    'depends': ['sale', 'product', 'purchase'],
    'data': [
        'views/custom_search_terms_common.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

