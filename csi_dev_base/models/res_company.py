from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = "res.company"
    
    custom_ach_template_id = fields.Many2one('mail.template', string='ACH Template', domain=[('model', '=', 'sale.order')])
    custom_ach_email_id = fields.Char(string='ACH Email')