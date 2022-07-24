# -*- coding: utf-8 -*-
{
    'name': "Helper de tolerie",

    'summary': """
        Gestion des matieres,
        Calculs des poids
            """,

    'description': """
        Addon ERP to manage sheetmetal production
    """,

    'author': "We S.A.",
    'website': "http://jc.ambert.free.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['metal_common','base','mrp','product',  'uom','website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/uom.xml',
        'data/product_categories.xml',
        'data/normative_body.xml',
        'data/material.xml',
        'data/profiles.xml',
        'data/settings.xml',
        'data/product_attribute.xml',
        'views/product/product_views.xml',
        'views/material/material_views.xml',
        'views/profile/profile_views.xml',
        'views/profile/profile_type_views.xml',
        # 'views/res_config_settings_view.xml',
        'views/product/product_attribute_views.xml',
        'views/product/product_category_views.xml',
        'menus/metal_menu.xml',
        # 'views/assets.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    # 'demo': ['data/mrp_plm_demo.xml'],
    
    #Module Installation
    'installable': True,
    'application': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
