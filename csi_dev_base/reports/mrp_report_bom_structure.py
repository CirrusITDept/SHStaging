# -*- coding: utf-8 -*-

from odoo import models

class ReportBomStructureCustom(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'
    
    def return_last_purchase_price(self, product_product_rec):
        order_line = self.env['purchase.order.line'].search([('product_id','=',product_product_rec.id)], order='create_date desc', limit=1)
        if order_line:
            return order_line.price_unit
        else:
            return 0

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        res = super(ReportBomStructureCustom, self)._get_bom(bom_id, product_id, line_qty, line_id, level)
        res['cust_last_purchase_price'] = self.return_last_purchase_price(res['product'])
        sum = 0
        for line in res['components']:
            sum = sum + line['cust_last_purchase_price']
        res['last_purchase_total'] = sum 
        return res

    def _add_last_purchase_price(self, components):
        for line in components:
            prod_id = line.get('prod_id')
            cost = 0
            if prod_id:
                prod_id = self.env['product.product'].browse(prod_id)
                cost = self.return_last_purchase_price(prod_id)
            line['cust_last_purchase_price'] = cost
        return True

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components, total = super(ReportBomStructureCustom, self)._get_bom_lines(bom, bom_quantity, product, line_id, level)
        self._add_last_purchase_price(components)
        return components, total