from odoo import models, fields, _
from odoo.exceptions import ValidationError
import json

class HelpDeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    def write(self, vals):
        res = super(HelpDeskTicket, self).write(vals)
        if 'stage_id' in vals:
            stage_id = vals['stage_id']
            helpdesk_stage = self.env['helpdesk.stage'].browse(stage_id)
            if helpdesk_stage.is_close:
                if not self.tag_ids:
                    raise ValidationError(_('Please add a tag before closing the ticket'))
        return res