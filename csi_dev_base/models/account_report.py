import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

def Reverse(lst):
    return [ele for ele in reversed(lst)]

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'
    
    @api.model
    def _init_filter_comparison(self, options, previous_options=None):
        super(AccountReport, self)._init_filter_comparison(options, previous_options)
        options['comparison']['periods'] = Reverse(options['comparison']['periods'])