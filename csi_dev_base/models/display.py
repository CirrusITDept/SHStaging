# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError

class DisplayDisplay(models.Model):

    _inherit = "display.display"

    def _get_won_sale(self):

        for display in self:
            One = 1

    def _get_move_lines(self, display):

        linked_picking = []
        for sale in self.env['sale.order'].search([('display_id','=',display.id)]):
            for picking in sale.picking_ids:
                linked_picking.append(picking.name)
        if linked_picking:
            move_line_ids = self.env['stock.move.line'].search([('reference', 'in', linked_picking), ('qty_done','>=',1)
                                                                   ,('state','=','done')])
            return move_line_ids
        return []

    def _get_shipped_line_count(self):
        for display in self:
            display.shipped_line_count = len(self._get_move_lines(display))

#    won_sale_id = fields.Many2one("sale.order", "Sale Order", compute="_get_won_sale")
    shipped_line_count = fields.Integer("Shipped line Count", compute='_get_shipped_line_count')
    custom_lock_display = fields.Boolean(string="Lock Display")

    def list_shipped_items(self):
        action = self.env.ref('csi_dev_base.csi_action_stock_move_line_tree_view').read()[0]
        action['views'] = [
            (self.env.ref('csi_dev_base.csi_stock_move_line_tree_view').id, 'tree'),
        ]
        action['context'] = self.env.context
        move_line_ids = self._get_move_lines(self)

        if move_line_ids:
            action['domain'] = [('id', 'in', move_line_ids.ids)]
        else:
            action['domain'] = [('id', '=', -1)]
        return action
    
    def write(self, vals):      
        if not 'custom_lock_display' in vals:  
            for display_rec in self:
                if display_rec.custom_lock_display:
                    raise ValidationError(_('Edit not allowed'))
        
        res = super(DisplayDisplay, self).write(vals)
        return res