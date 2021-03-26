# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class MrpBom(models.Model):
    _inherit = "mrp.bom"
    
    custom_refurbish = fields.Boolean(string="Refurbish",track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    product_tmpl_id = fields.Many2one(track_visibility='onchange')
    product_id = fields.Many2one(track_visibility='onchange')
    product_qty = fields.Float(track_visibility='onchange')
    product_uom_id = fields.Many2one(track_visibility='onchange')
    product_uom_category_id = fields.Many2one(track_visibility='onchange')
    sequence = fields.Integer(track_visibility='onchange')
    routing_id = fields.Many2one(track_visibility='onchange')
    ready_to_produce = fields.Selection(track_visibility='onchange')
    picking_type_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    consumption = fields.Selection(track_visibility='onchange')
    
    @api.onchange('custom_refurbish')
    def onchange_custom_refurbish(self):
        if self.custom_refurbish:
            picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'mrp_operation'),('name', '=', 'Refurbishing')], limit=1)
            if picking_type_id:
                self.picking_type_id = picking_type_id.id