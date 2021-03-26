# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    custom_box_qty = fields.Integer(string="Box Qty")