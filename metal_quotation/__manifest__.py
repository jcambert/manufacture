# -*- coding: utf-8 -*-
{
    'name': "Devis Tolerie",

    'summary': """
        Calcul des prix de revient
            """,

    'description': """
        Addon ERP to manage sheetmetal quotation
    """,

    'author': "We S.A.",
    'website': "http://jc.ambert.free.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['metal'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'security/quotation_security.xml',
        'security/ir.model.access.csv',
       
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    # 'demo': ['data/mrp_plm_demo.xml'],
    
    #Module Installation
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
