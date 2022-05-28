# -*- coding: utf-8 -*-
{
    'name': "Gestion de cycle de vie des produits",

    'summary': """
        PLM, ECOs, Versions
        this application manages the life cycle of products
        with the following features:    
            - Versions management
            - ECOs management
            - PLM management
            - ...
            """,

    'description': """
        Addon ERP to manage PLM 
    """,

    'author': "We S.A.",
    'website': "http://jc.ambert.free.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['base','mrp','product','sale', 'mail', 'uom'],

    # always loaded
    'data': [
        'security/plm_security.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    # 'demo': ['data/mrp_plm_demo.xml'],
    
    #Module Installation
    'installable': True,
    'application': True,
    'auto_install': False
}
