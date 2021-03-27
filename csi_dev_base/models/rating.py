from odoo import api, fields, models

class Rating(models.Model):
    _name = "rating.rating"
    _inherit = ['rating.rating','mail.thread', 'mail.activity.mixin']    