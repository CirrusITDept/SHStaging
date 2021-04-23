# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'CSI Dev Base',
    'summary': 'This module show the status of the helpdesk tickets for different stages in dashboard view.',
    'version': '13.0.0.1.21',
    'category': 'Helpdesk',
    'author': 'Himanshu Mittal',
    'maintainer': 'Himanshu Mittal',
    'website': 'Himanshu Mittal',
    'license': 'AGPL-3',
    'depends': ['helpdesk'
                ,'base_csi'
                ,'sale_crm'
                ,'stock'
                ,'csi_so_mods'
                ,'stock_barcode'
                ,'crm'
                ,'quality'
                ,'rating'
                ,'account_reports'
                ,'open_in_new_tab'
                ,'many2many_tags_link'
                ,'sale_stock'],
    'data': [
        'data/csi_mail_template_data.xml'
        ,'security/csi_dev_base_security.xml'
        ,'data/order_delivered_email_template.xml'
        ,'data/order_shipped_email_template.xml'
        ,'data/signed_quote_email_template.xml'
        ,'data/thank_you_for_your_purchase_template.xml'
        ,'data/ir_cron.xml'
        ,'views/helpdesk_view.xml'
        ,'views/helpdesk_team.xml'
        ,'views/display_view.xml'
        ,'views/assets.xml'
        ,'views/stock_picking_view.xml'
        ,'views/res_partner_view.xml'
        ,'views/product_view.xml'
        ,'views/crm_lead_views.xml'
        ,'views/rating_view.xml'
        ,'views/mrp_view.xml'
        ,'views/stock_move.xml'
        ,'views/sale_portal_templates.xml'
        ,'views/res_company_view.xml'
        ,'views/sale_order_view.xml'
        ,'reports/report_deliveryslip.xml'
        ,'reports/mrp_report_bom_structure.xml'
        ,'security/ir.model.access.csv'
    ],
    'qweb' : ['static/src/xml/*.xml'],
    'application': False,
    'installable': True,
    'auto_install': False,
}