{
    'name': 'Project Team',
    'author': 'Ogroni Informatix Limited',
    'version': '1.0',
    'summary': 'Project Team',
    'sequence': 15,
    'description': """
Project Team
    """,
    'category': 'Custom Search Terms',
    'website': 'https://ogroni.com/',
    'depends': ['base', 'hr', 'product', 'analytic', 'portal', 'digest', 'sale', 'purchase', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_views_inherit.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
