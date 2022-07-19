# -*- coding: utf-8 -*-
{
    'name': "Bibliothèque de fonctions Manufacture",

    'summary': """
        Mixin Models for Manufacturing
            """,

    'description': """
        Addon ERP pour la gestion de la manufacture
    """,

    'author': "We S.A.",
    'website': "http://jc.ambert.free.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    # 'demo': ['data/mrp_plm_demo.xml'],
    
    #Module Installation
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}
