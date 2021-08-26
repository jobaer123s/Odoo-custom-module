# -*- coding: utf-8 -*-
{
    'name': 'Web Debranding',
    'version': '1.0.0',
    'category': 'Web',
    'sequence': 1,
    'summary': 'Web Debranding for Odoo v13',
    'description': """Web Debranding for Odoo v13""",
    'author': 'Ogroni Informatix Limited',
    'company': 'Ogroni Informatix Limited',
    'maintainer': 'Ogroni Informatix Limited',
    'website': "https://ogroni.net/",
    'depends': ['web'],
    'data': [
        'security/change_passwd_security.xml',
        'views/webclient_templates.xml',
        'views/login_template.xml',
        'views/menu_color.xml',
        'views/change_passwd.xml',
    ],
    'qweb': ['static/src/xml/base.xml'],
    'bootstrap': True,
    'installable': True,
    'application': True,
    'auto_install': False,
}

