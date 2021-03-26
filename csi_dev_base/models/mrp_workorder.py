from odoo import api, fields, models, _

class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.workorder'
    
    def record_production(self):
        res = super(MrpProductionWorkcenterLine, self).record_production()
        print('here 1')
        #self.production_id.post_inventory()
