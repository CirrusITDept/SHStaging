from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move.line"

    def unlink_line_assoc_lines(self):
        records_to_unlink = self.env["stock.move.line"]
        for record in self:
            production_order = record.move_id.production_id
            lines = production_order.move_raw_ids.mapped("move_line_ids")
            for l in lines:
                if record.lot_id.id in l.lot_produced_ids.ids:
                    records_to_unlink |= l
            records_to_unlink |= record
        records_to_unlink.unlink()
