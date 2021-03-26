# -*- coding: utf-8 -*-

from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def create(self, values):
        return super(SaleOrder, self).create(values)
    
    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        fedex_ground = self.env['delivery.carrier'].search([('name', '=', 'FedEx Ground®')],limit=1)
        if fedex_ground:
            rec['carrier_id'] = fedex_ground.id
        
        team_id = self.env['crm.team'].search([('member_ids', 'in', self.env.uid)], limit=1).id
        if team_id:
            rec['team_id'] = team_id
        return rec
    
    def action_confirm(self):
        if self.is_billable == False:
            vals = {}
            vals['price_unit'] = 0
            for line in self.order_line:
                line.update(vals)
            
        res = super(SaleOrder, self).action_confirm()
        return res
    
    custom_ach_info_rec = fields.Boolean('ACH Info Received', track_visibility="onchange")

    def get_sale_order(self,cust_bank_name,cust_acc_number,cust_rout_number,cust_acc_holder):
        order = self.env['sale.order'].sudo().browse(int(self.id))
        if order and cust_bank_name:
            mail_template_id = order.company_id.custom_ach_template_id
            if mail_template_id and order.company_id.custom_ach_email_id:
                values = mail_template_id.generate_email(order.id)
                body_string = values['body']
                body_string = body_string.replace('cust_bank_name',cust_bank_name)
                body_string = body_string.replace('cust_acc_number',cust_acc_number)
                body_string = body_string.replace('cust_rout_number',cust_rout_number)
                body_string = body_string.replace('cust_acc_holder',cust_acc_holder)
                value = {
                        'email_to': order.company_id.custom_ach_email_id,
                        'subject': mail_template_id.subject,
                        'res_id': order.id,
                        'body_html': body_string
                    }
                mail_template_id.send_mail(order.id,  force_send=True, email_values=value)
                order.update({'custom_ach_info_rec':True}) 