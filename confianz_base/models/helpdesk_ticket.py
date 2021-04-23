# -*- coding: utf-8 -*-

from odoo import fields, models, api

class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    install_date_auto_update = fields.Boolean(string="Update Install Date")

HelpdeskTeam()

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    partner_id = fields.Many2one(required=False)
    partner_name = fields.Char(required=False)
    partner_email = fields.Char(required=False)
    partner_phone = fields.Char(required=False)

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id.is_close and self.team_id.install_date_auto_update:
            if not self.display_id.install_date:
                self.display_id.install_date = fields.Date.today()
        return {}

    @api.onchange('display_id')
    def _onchange_display_id(self):
        if self.display_id:
            self.partner_sign_id = self.display_id.sign_shop
#            self.partner_end_id = self.display_id.end_user_contact
        return {}

HelpdeskTicket()