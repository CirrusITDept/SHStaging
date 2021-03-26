# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields
import json

class HelpDesk(models.Model):

    _inherit = 'helpdesk.team'

    stage_counts_ids = fields.Text(string="Stage Counts", compute="_get_stage_count_info")

    def _get_stage_count_info(self):

        for team in self:
            team_data = []
            for stage in self.env['helpdesk.stage'].search([]):
                if team.id in stage.team_ids.ids:
                    counts = self.env['helpdesk.ticket'].search_count(
                        [('stage_id', '=', stage.id), ('team_id', '=', team.id)])
                    team_data.append({'team_id':team.id,'stage_name':stage.name,'stage_id':stage.id, 'counter':counts})
            team.stage_counts_ids = json.dumps(team_data)

class StageCount(models.Model):

    _name = 'stage.count.info'
    _description = 'Stage Counter'

    _rec_name = 'stage_id'

    team_id = fields.Many2one("helpdesk.team", "Team")
    stage_id = fields.Many2one("helpdesk.stage", "Stage")
    counter = fields.Integer("Counter")

