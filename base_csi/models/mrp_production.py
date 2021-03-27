# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    display_id = fields.Many2one("display.display", string="Display")

    def open_quick_produce_wizard(self):
        self.ensure_one()
        action = self.env.ref("base_csi.open_quick_produce_action").read()[0]
        action["context"] = {
            "default_production_id": self.id,
        }
        return action


class MrpProductionQuickProduce(models.TransientModel):
    _name = "quick.produce"
    _description = "Quick Production Wizard"

    scan_ids = fields.Many2many("quick.produce.scan", string="Scan Serial #s")
    production_id = fields.Many2one("mrp.production", string="Production Order")

    def produce(self):
        for record in self:
            if not record.production_id:
                raise UserError(
                    "Seems there is no production order linked to this wizard."
                )
            for sn in record.scan_ids:
                lot = record.env["stock.production.lot"].search(
                    [
                        ("name", "=", sn.name),
                        ("product_id", "=", record.production_id.product_id.id),
                    ]
                )
                if not lot:
                    lot = record.env["stock.production.lot"].create(
                        {
                            "name": sn.name,
                            "product_id": record.production_id.product_id.id,
                            "company_id": self.env.user.company_id.id,
                        }
                    )
                produce_wiz = (
                    record.env["mrp.product.produce"]
                    .with_context(default_production_id=record.production_id.id)
                    .create({})
                )
                produce_wiz.finished_lot_id = lot.id
                produce_wiz.qty_producing = 1
                line_values = produce_wiz._update_workorder_lines()
                for values in line_values["to_create"]:
                    record.env["mrp.product.produce.line"].create(values)
                produce_wiz._record_production()


class MrpProductionQuickProduceScan(models.TransientModel):
    _name = "quick.produce.scan"
    _description = "Quick Production Wizard"

    name = fields.Char(string="Name")
