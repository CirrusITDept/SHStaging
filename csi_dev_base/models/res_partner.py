# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    custom_assigned_sign_shop = fields.Many2one('res.partner', domain=[('sign_shop','=',True)], string="Assigned Sign Shop", default=False)