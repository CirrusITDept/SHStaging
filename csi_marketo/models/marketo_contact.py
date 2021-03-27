# -*- coding: utf-8 -*-

from odoo import fields, models, _

class MarketoContact(models.Model):
    _name = "marketo.contact"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Marketo Contact"

    parse_error = fields.Char(string="Parse Error")
    parse_msg = fields.Char(string="Parse Message")
    done = fields.Char(string="Completed")
    odoo_id = fields.Many2one('res.partner', string="Odoo ID")
    full_name = fields.Char(string="Full Name")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    email = fields.Char(string="Email")
    street1 = fields.Char(string="Street 1")
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="Street 2")
    state_id = fields.Char(string="State")
    zip = fields.Char(string="Zip")
    phone = fields.Char(string="Phone")
    sale_id = fields.Many2one('res.users', string='Salesperson')
    parent_id = fields.Many2one('res.partner', string="Parent ID")