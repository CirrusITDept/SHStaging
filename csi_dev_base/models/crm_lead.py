# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = "crm.lead"
    
    @api.depends('custom_calc_reve','order_ids','order_ids.amount_total')
    def _compute_calc_reve(self):
        for lead in self:
            orders = self.env['sale.order'].search([('opportunity_id','=',lead.id)])
            if orders:
                count = 0
                sum = 0
                for order in orders:
                    count = count + 1
                    sum = sum + order.amount_total                 
                lead.custom_calc_reve = sum / count
                lead.custom_pro_reve = lead.custom_calc_reve * lead.probability
                lead.custom_pro_reve = lead.custom_pro_reve / 100
            else:
                lead.custom_calc_reve = 0
                lead.custom_pro_reve = 0
    
    @api.depends('write_date')
    def _def_custom_last_modified(self):
        for lead in self:
            if not lead.custom_last_modified:
                lead.custom_last_modified = lead.write_date
                lead.custom_last_updated_by = lead.write_uid
            elif lead.write_uid != self.env.ref('base.user_root').id:
                lead.custom_last_modified = lead.write_date
                lead.custom_last_updated_by = lead.write_uid
                
    def _compute_custom_salesperson_change(self):
        """
        Compute a field indicating whether the current user
        shouldn't be able to edit some fields.
        """
        if self.user_has_groups('csi_dev_base.group_can_change_salesperson'):
            self.custom_salesperson_change = True
        else:
            if self.stage_id.name == 'Quote Requested':
                self.custom_salesperson_change = True
            else:
                self.custom_salesperson_change = False
    
    custom_salesperson_change = fields.Boolean(compute="_compute_custom_salesperson_change")
    custom_assigned_sign_shop = fields.Many2one('res.partner', related="partner_id.custom_assigned_sign_shop")
    custom_calc_reve = fields.Float(compute="_compute_calc_reve", string="Calculated Revenue", readonly=True, store=True)
    custom_pro_reve = fields.Float(compute="_compute_calc_reve", string="Pro-Rated Revenue", readonly=True, store=True)
    custom_last_modified = fields.Datetime(string="Z - Last Modified On", compute="_def_custom_last_modified", store=True)
    custom_last_updated_by = fields.Many2one('res.users', string='Z - Last Updated by')
    
    def write(self, vals):
        if self.env.user.id != self.env.ref('base.user_root').id:
            vals['custom_last_modified'] = fields.Datetime.now()
            vals['custom_last_updated_by'] = self.env.user.id 
        res = super(CrmLead, self).write(vals)
        return res
    
    def action_sale_quotations_sign_shop(self):
        action = self.env.ref("sale_crm.sale_action_quotations_new").read()[0]
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'search_default_partner_id': self.partner_id.custom_assigned_sign_shop.id,
            'default_partner_id': self.partner_id.custom_assigned_sign_shop.id,
            'default_team_id': self.team_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_client_order_ref': self.partner_id.name
        }
        return action