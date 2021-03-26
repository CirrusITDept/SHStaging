# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Repair(models.Model):
    _inherit = "repair.order"

    operations = fields.One2many(readonly=False, states={"done": [("readonly", True)]})
    fees_lines = fields.One2many(readonly=False, states={"done": [("readonly", True)]})


class RepairLine(models.Model):
    _inherit = "repair.line"

    @api.onchange("type", "repair_id")
    def onchange_operation_type(self):
        """ GFP: Inherit base function to add default repair locations
        """
        if self.repair_id.company_id.repair_location_id:
            repair_loc = self.repair_id.company_id.repair_location_id
        else:
            repair_loc = (
                self.env["stock.location"]
                .search([("usage", "=", "production")], limit=1)
                .id
            )
        if not self.type:
            self.location_id = False
            self.location_dest_id = False
        elif self.type == "add":
            self.onchange_product_id()
            args = (
                self.repair_id.company_id
                and [("company_id", "=", self.repair_id.company_id.id)]
                or []
            )
            warehouse = self.env["stock.warehouse"].search(args, limit=1)
            self.location_id = warehouse.lot_stock_id
            self.location_dest_id = repair_loc
        else:
            self.price_unit = 0.0
            self.tax_id = False
            self.location_id = repair_loc
            self.location_dest_id = (
                self.env["stock.location"]
                .search([("scrap_location", "=", True)], limit=1)
                .id
            )
