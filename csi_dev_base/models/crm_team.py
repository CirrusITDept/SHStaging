# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class CrmTeam(models.Model):
    _inherit = "crm.team"

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None, domain=None):
        if not user_id:
            user_id = self.env.uid
        team_id = self.env['crm.team'].search([
            '|', ('user_id', '=', user_id), ('member_ids', '=', user_id),
            '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id)
        ], limit=1)
        if not team_id and 'default_team_id' in self.env.context:
            team_id = self.env['crm.team'].browse(self.env.context.get('default_team_id'))
        if 'default_1team_id' in self.env.context:
            if self.env.context.get('default_1team_id'):
                team_id = self.env['crm.team'].browse(self.env.context.get('default_1team_id'))
        if not team_id:
            team_domain = domain or []
            default_team_id = self.env['crm.team'].search(team_domain, limit=1)
            return default_team_id or self.env['crm.team']
        return team_id