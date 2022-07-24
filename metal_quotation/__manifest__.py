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
    'depends': ['metal','mrp'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'security/quotation_security.xml',
        'security/ir.model.access.csv',
        'actions/quotation_actions.xml',
        'actions/product_actions.xml',
        'actions/workcenter_actions.xml',
        'views/quotation/metal_quotation_template_view_form.xml',
        'views/quotation/metal_quotation_view_form.xml',
        'views/product/metal_product_form_view.xml',
        'views/workcenter/metal_wokcenter_form_view.xml',
        'views/workcenter/metal_workcenter_cutting_speed_tree_view.xml',
        'actions/quotation_menus_actions.xml',
        'menus/quotation_menu.xml',
       
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
