# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    new_del_qty = fields.Float('New Delivery Qty')
    
    def _get_not_done_delivery_order_qty(self):
        self.ensure_one()
        qty = 0.0
        for move in self.move_ids.filtered(lambda r: r.state not in ('done','cancel') and not r.scrapped):
            if move.location_dest_id.usage == "customer":
                if not move.origin_returned_move_id:
                    qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)
        return qty        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
