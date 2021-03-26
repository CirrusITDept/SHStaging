from odoo import api, fields, models, SUPERUSER_ID, _

class QualityAlert(models.Model):
    _inherit = "quality.alert"
    
    x_studio_return_order = fields.Many2one('stock.picking', string="Return Order")