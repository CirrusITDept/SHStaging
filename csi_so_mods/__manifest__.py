# -*- coding: utf-8 -*-
{
    'name': "CSI SO Mods",
    'summary': """
        Sales Order Modifications""",
    'description': """
       SO stuff anf Helpdesk. 
    """,
    'author': "Cirrus LED",
    'website': "http://www.cirrusled.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Custom',
    'version': '13.0.3',
    'application': False,
    'installable' : True,
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'base_csi'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}