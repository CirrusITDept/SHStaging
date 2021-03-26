from odoo import api, fields, models, SUPERUSER_ID, _

class CustomStockMove(models.Model):
    _name = "custom.stock.move"
    _description = "Custom Stock Move"
    
    description_picking = fields.Text('Description of Picking')
    product_id = fields.Many2one( 'product.product', 'Product', check_company=True, domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", index=True, required=True)
    product_uom_qty = fields.Float('Done', digits='Product Unit of Measure', default=0.0, required=True)
    product_uom_qty_initial = fields.Float('Initial Demand',digits='Product Unit of Measure', default=0.0)
    picking_id = fields.Many2one('stock.picking', 'Transfer Reference', index=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    @api.model
    def create(self, values):
        if 'move_id' in values and 'picking_id' in values:
            if values['picking_id'] and not values['move_id']:
                obj_product_rec = self.env["product.product"].browse(values['product_id'])
                if obj_product_rec.tracking == 'none':
                    cust_vals = {
                                    "description_picking" : obj_product_rec.name,
                                    "product_id" : values['product_id'],
                                    "product_uom_qty" : values['qty_done'],
                                    "picking_id" : values['picking_id'],
                                    "product_uom_id" : values["product_uom_id"],
                                    "product_uom_qty_initial" : 0.0
                    }        
                    self.env["custom.stock.move"].create(cust_vals)
                else:
                    custom_move_rec = self.env['custom.stock.move'].search([('picking_id', '=', values['picking_id']),('product_id', '=', values['product_id'])], limit=1)
                    if custom_move_rec:
                        custom_move_rec.product_uom_qty = custom_move_rec.product_uom_qty + 1 
                    else:
                        cust_vals = {
                                    "description_picking" : obj_product_rec.name,
                                    "product_id" : values['product_id'],
                                    "product_uom_qty" : values['qty_done'],
                                    "picking_id" : values['picking_id'],
                                    "product_uom_id" : values["product_uom_id"],
                                    "product_uom_qty_initial" : 0.0
                        }        
                        self.env["custom.stock.move"].create(cust_vals)                                        
        return super(StockMoveLine, self).create(values)
    
    @api.model
    def write(self, values):
        res = super(StockMoveLine, self).write(values)
        if 'qty_done' in values:
            for line in self:
                if line.picking_id and not line.move_id:
                    custom_move_rec = self.env['custom.stock.move'].search([('picking_id', '=', line.picking_id.id),('product_id', '=', line.product_id.id)], limit=1)
                    if custom_move_rec:
                        custom_move_rec.product_uom_qty = values['qty_done']
                    
        return res