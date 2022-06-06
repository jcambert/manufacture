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
        'views/eco/mrp_eco_kanban.xml',
        'views/eco/mrp_eco_search.xml',
        'views/eco/mrp_eco_view_calendar.xml',
        'views/eco/mrp_eco_view_form.xml',
        'views/eco/mrp_eco_view_graph.xml',
        'views/eco/mrp_eco_view_pivot.xml',
        'views/eco/mrp_eco_view_tree.xml',
        'views/eco_bom_change/mrp_eco_bom_change_view_form.xml',
        'views/eco_routing_change/mrp_eco_routing_change_view_form.xml',
        'views/eco_stage/mrp_eco_stage_view_form.xml',
        'views/eco_stage/mrp_eco_stage_kanban.xml',
        'views/eco_stage/mrp_eco_stage_view_tree.xml',
        'views/eco_tag/mrp_eco_tag_view_search.xml',
        'views/eco_tag/mrp_eco_tag_view_tree.xml',
        'views/eco_type/mrp_eco_type_view_form.xml',
        'views/eco_type/mrp_eco_type_view_kanban.xml',
        'views/eco_type/mrp_eco_type_view_tree.xml',
        'views/eco_type/mrp_eco_type_dashboard_view_kanban.xml',
        'actions/mrp_menus_actions.xml',
        'menus/mrp_menu.xml',
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
