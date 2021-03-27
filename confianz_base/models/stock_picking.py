from odoo import fields, models, api
from datetime import datetime, timedelta

class StockPicking(models.Model):
    _inherit = "stock.picking"

    scheduled_date = fields.Datetime(default=datetime.now() + timedelta(days=45))
