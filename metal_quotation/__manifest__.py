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
    'depends': ['metal','mrp','web'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'security/quotation_security.xml',
        'security/ir.model.access.csv',
        'actions/quotation_actions.xml',
        'actions/product_actions.xml',
        'actions/workcenter_actions.xml',
        'actions/component_actions.xml',
        'actions/material_actions.xml',
        'actions/operation_actions.xml',
        'actions/calculate_actions.xml',
        'wizards/add_material_template_to_quotation_view.xml',
        'wizards/add_operation_template_to_quotation_view.xml',
        'wizards/add_product_to_quotation_view.xml',
        'wizards/add_component_template_to_quotation_view.xml',
        'views/quotation/metal_quotation_template_view_form.xml',
        'views/quotation/metal_quotation_view_form.xml',
        'views/quotation/metal_quotation_view_tree.xml',
        'views/operation/metal_operation_template_view_tree.xml',
        'views/operation/metal_operation_template_view_form.xml',
        'views/operation/metal_operation_view_tree.xml',
        'views/operation/metal_operation_view_form.xml',
        'views/product/metal_product_form_view.xml',
        'views/product/metal_product_tree_view.xml',
        'views/product/metal_product_line_form_view.xml',
        'views/product/metal_product_line_tree_view.xml',
        'views/product/metal_product_price_form_view.xml',
        'views/component/metal_component_form_view.xml',
        'views/component/metal_component_tree_view.xml',
        'views/component/metal_component_template_form_view.xml',
        'views/component/metal_component_template_tree_view.xml',
        'views/workcenter/metal_wokcenter_form_view.xml',
        'views/workcenter/metal_workcenter_cutting_speed_tree_view.xml',
        'views/material/metal_material_form_view.xml',
        'views/material/metal_material_tree_view.xml',
        'views/material/metal_material_template_form_view.xml',
        'views/material/metal_material_template_tree_view.xml',
        'views/calculate/metal_calculation_format_template_form_view.xml',
        'views/calculate/metal_calculation_form_view.xml',
        'views/calculate/metal_calculation_tree_view.xml',
        'views/calculate/metal_calculation_cutting_form_view.xml',
        'views/calculate/metal_calculation_cutting_tree_view.xml',
        'actions/quotation_menus_actions.xml',
        'menus/quotation_menu.xml',
        'reports/quotation_report.xml',
        'reports/report.xml',
        'data/materials_data.xml',
        'data/components_data.xml',
        'data/formats_data.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    # 'demo': ['data/mrp_plm_demo.xml'],
    
    #Module Installation
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': '_quotation_post_init',
    'license': 'LGPL-3',
}

