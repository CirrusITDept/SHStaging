# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)

class CustomerPortal(CustomerPortal):

    @http.route(['/my/orders/ach/capture'], type='json', auth="public", website=True)
    def ach_capture(self, os_id=None, cust_bank_name=None, cust_acc_number=None, cust_rout_number=None, cust_acc_holder=None, cust_e_check=None):
        if os_id:
            order = request.env['sale.order'].sudo().browse(int(os_id))
            if order and cust_bank_name:
                mail_template_id = order.company_id.custom_ach_template_id
                if mail_template_id and order.company_id.custom_ach_email_id:
                    values = mail_template_id.generate_email(order.id)
                    body_string = values['body']
                    body_string = body_string.replace('cust_bank_name',cust_bank_name)
                    body_string = body_string.replace('cust_acc_number',cust_acc_number)
                    body_string = body_string.replace('cust_rout_number',cust_rout_number)
                    body_string = body_string.replace('cust_acc_holder',cust_acc_holder)
                    body_string = body_string.replace('cust_e_check',str(cust_e_check))
                    value = {
                            'email_to': order.company_id.custom_ach_email_id,
                            'subject': mail_template_id.subject,
                            'res_id': order.id,
                            'body_html': body_string
                        }
                    mail_template_id.send_mail(order.id,  force_send=True, email_values=value)
                    order.update({'custom_ach_info_rec':True}) 