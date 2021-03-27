# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class delivery_create_wizard(models.TransientModel):
    _name = "delivery.create.wizard"
    
    name = fields.Many2one('sale.order',string='Sale Order')
    sale_delivery_line_ids = fields.One2many('sale.delivery.line.wizard','delivery_create_id', string='Sale Delivery Lines')
    
    @api.model
    def default_get(self,vals):
        vals = super(delivery_create_wizard,self).default_get(vals)
        sale_pool = self.env['sale.order']
        sale_id = sale_pool.browse(self._context.get('active_id'))
        if sale_id.state != 'sale':
            raise ValidationError("Delivery order create only in 'Sale order' State")
        line_val=[]
        for line in sale_id.order_line:
            qty = line.product_uom_qty - line.qty_delivered
            del_qty = line._get_not_done_delivery_order_qty()
            qty = qty - del_qty
            if qty > 0:
                line_val.append((0,0,{
                                'product_id':line.product_id.id,
                                'name':line.name,
                                'sale_line_id':line.id,
                                'order_qty':qty,
                                'quantity':qty,
                            }))
             
        vals.update({
            'name':sale_id.id,
            'sale_delivery_line_ids':line_val,
        })
        return vals

    def create_delivery_order(self):
        for line in self.sale_delivery_line_ids:
            line.sale_line_id.new_del_qty = line.quantity
            if line.order_qty < line.quantity:
                raise ValidationError("%s product Quatity must be less or equal to %s " % (line.product_id.name, line.order_qty))
            if line.sale_line_id:
                line.sale_line_id._action_launch_stock_rule()
        
        for line in self.name.order_line:
            line.new_del_qty = 0


class sale_delivery_line_wizard(models.TransientModel):
    _name = 'sale.delivery.line.wizard'

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', string='Product')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Line')
    quantity = fields.Float('Quantity')
    order_qty = fields.Float('Order Quntity')
    delivery_create_id = fields.Many2one('delivery.create.wizard', string='Delivery Wizard')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: