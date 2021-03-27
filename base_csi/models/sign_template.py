# -*- coding: utf-8 -*-
from odoo import models, fields


class SignTemplate(models.Model):
    _inherit = "sign.template"

    sale_id = fields.Many2one("sale.order", string="Sale Order")