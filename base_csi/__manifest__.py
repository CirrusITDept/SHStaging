# -*- coding: utf-8 -*-

###################################################################################
#
#    Copyright (C) 2019 GFP Solutions LLC
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

{
    "name": "Base Developments for Cirrus LED",
    "category": "Hidden",
    "author": "GFP Solutions LLC",
    "summary": "Custom",
    "version": "13.3.23",
    "description": """
THIS MODULE IS PROVIDED AS IS - INSTALLATION AT USERS' OWN RISK -
AUTHOR OF MODULE DOES NOT CLAIM ANY
RESPONSIBILITY FOR ANY BEHAVIOR ONCE INSTALLED.
        """,
    "depends": [
        "account_accountant",
        "sale_stock",
        "delivery",
        "helpdesk",
        "crm",
        "quality",
        "quality_control",
        "mrp",
        "purchase",
        "repair",
        "sign",
        "stock_barcode",
        "helpdesk_repair",
    ],
    "data": [
        "data/data.xml"
        ,"security/ir.model.access.csv"
        ,"views/purchase_view.xml"
        ,"views/ir_actions_act_window.xml"
        ,"views/stock_view.xml"
        ,"views/repair_view.xml"
        ,"views/sign_view.xml"
        ,"views/display_view.xml"
        ,"views/delivery_view.xml"
        ,"views/ir_ui_views.xml"
        ,"views/res_company_view.xml"
        ,"views/res_users_view.xml"
        ,"views/res_config_view.xml"
        ,"views/helpdesk_ticket.xml"
        ,"views/res_partner_view.xml"
        ,"views/sale_order_view.xml"
        ,"views/salesforce_view.xml"
        ,"views/crm_view.xml"
        ,"views/shipstation_view.xml"
        ,"views/product_view.xml"
        ,"views/account_view.xml"
        ,"views/quality_alert_view.xml"
        ,"views/mrp_view.xml"
        ,"views/quick_produce_view.xml"
        ,"views/ir_ui_menu.xml"
        ,"views/base_csi_templates.xml"
        ,"reports/paper_format.xml"
        ,"reports/templates.xml"
    ],
    "installable": True,
    "qweb": ["static/src/xml/thread.xml", "static/src/xml/qweb_template.xml"],
}
