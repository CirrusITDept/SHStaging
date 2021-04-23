from odoo import api, fields, models, SUPERUSER_ID, _
from lxml import etree

import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = "stock.picking"

    custom_move_lines = fields.One2many('custom.stock.move', 'picking_id', string="Additional Products", copy=True)
    custom_quality_alert = fields.One2many('quality.alert', 'x_studio_return_order', string="Quality Alert")
    sale_id = fields.Many2one(copy=True)
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Picking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type =='form':
            if (not self.user_has_groups('csi_dev_base.group_can_adjust_inventory')):
                virtual_location_id = self.env.ref('stock.stock_location_locations_virtual').id
                doc = etree.fromstring(res['arch'])
                for node in doc.xpath("//field[@name='location_id']"):
                    user_filter =  "[('company_id','in',[company_id, False]),('id','not in',[" + str(virtual_location_id) + "]),'!',('id','child_of'," + str(virtual_location_id) + ")]"
                    node.set('domain',user_filter)
                    res['arch'] = etree.tostring(doc)
                
                for node in doc.xpath("//field[@name='location_dest_id']"):
                    user_filter =  "[('company_id','in',[company_id, False]),('id','not in',[" + str(virtual_location_id) + "]),'!',('id','child_of'," + str(virtual_location_id) + ")]"
                    node.set('domain',user_filter)
                    res['arch'] = etree.tostring(doc)
        return res
    
    def write(self, values):
        res = super(Picking, self).write(values)
        if 'sale_id' in values:
            if not self.group_id:
                order_rec = self.env['sale.order'].browse(values['sale_id'])
                if order_rec:
                    proc_group_rec = self.env['procurement.group'].search([('name', '=', order_rec.name)], limit=1)
                    if proc_group_rec:
                        stock_move_recs = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
                        for stock_move_rec in stock_move_recs:
                            stock_move_rec.group_id = proc_group_rec.id 
                        values['group_id'] = proc_group_rec.id 
        return res
    
    def action_confirm(self):
        res = super(Picking, self).action_confirm()
        for picking in self:
            if picking.sale_id and not picking.group_id:
                proc_group_rec = self.env['procurement.group'].search([('name', '=', picking.sale_id.name)], limit=1)
                if proc_group_rec:
                    stock_move_recs = self.env['stock.move'].search([('picking_id', '=', picking.id)], limit=1)
                    for stock_move_rec in stock_move_recs:
                        stock_move_rec.group_id = proc_group_rec.id 
                    picking.group_id = proc_group_rec.id
        return res
    
    @api.model
    def _run_custom_return_picking_update(self):
        _logger.info("Running - 'Return Picking Details update' Cron - Start")
        
        picking_obj = self.env["stock.picking"]
        pickings = picking_obj.search([
                ("return_picking_id", "!=", False),
                ("return_picking_id.state", "not in", ["done","cancel"]),
                ("return_picking_id.carrier_tracking_ref", "=", False),
                ("state", "in", ["done"]),
            ])
        for picking in pickings:
            new_sched_date = picking.date_done + timedelta(days=45)
            
            picking.return_picking_id.carrier_tracking_ref = picking.return_carrier_tracking_ref
            picking.return_picking_id.scheduled_date = new_sched_date 
        
        _logger.info("Running - 'Return Picking Details update' Cron - End")
        
    def _create_backorder(self):
        backorders = super(Picking, self)._create_backorder()
        
        for picking in self:
            for backorder in backorders:
                if backorder.backorder_id.id == picking.id:
                    backorder.sale_id = picking.sale_id.id
                    break