# -*- coding: utf-8 -*-
# Copyright 2020, Confianz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Confianz Base',
    'version': '13.0',
    'category': 'Sales',
    'summary': "Sales",
    'description': """
Extension on Sale module to calculate profit margin on Sale Order.
=====================================================================================================
Extension on Sale module to calculate profit margin on Sale Order.
       """,
    'author': 'Confianz Global',
    'website': 'https://confianzit.com',
    'images': [],
    'data': [
                "views/helpdeak_view.xml",
            ],
    'depends': ['sale'
                ,'helpdesk'
                ,'base_csi'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
