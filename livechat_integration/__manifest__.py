# -*- coding: utf-8 -*-
{
    'name': 'Live chat Controller',
    'version': '12.0.1.0.0',
    'summary': "Live chat Controller",
    'category': 'Website',
    'author': 'Confianz',
    'maintainer': 'Confianz',
    'company': 'Confianz',
    'website': 'https://www.confianzit.com',
    "depends": ['base', 'website_livechat','im_livechat'],
    'data': [
        'views/live_chat_log.xml',
        'views/live_chat_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
