from odoo import models

import logging

_logger = logging.getLogger(__name__)


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super(Orderpoint, self)._quantity_in_progress()
        for poline in self.env["purchase.order.line"].search(
            [
                (
                    "state",
                    "in",
                    (
                        "to approve",
                        "approved_sent",
                        "approved",
                        "2approved",
                        "1approved",
                    ),
                ),
                ("orderpoint_id", "in", self.ids),
            ]
        ):
            res[poline.orderpoint_id.id] += poline.product_uom._compute_quantity(
                poline.product_qty, poline.orderpoint_id.product_uom, round=False
            )
        return res
