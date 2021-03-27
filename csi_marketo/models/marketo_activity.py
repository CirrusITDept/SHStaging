# -*- coding: utf-8 -*-

from odoo import fields, models, _

class MarketoActivity(models.Model):
    _name = "marketo.activity"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Marketo Activity"

    parse_error = fields.Char(string="Parse Error")
    done = fields.Char(string="Completed")
    lead_id = fields.Many2one('res.partner', string="Odoo Lead")
    body = fields.Html(string="Body", translate=False)
    user_id = fields.Many2one('res.users', string='User Id')