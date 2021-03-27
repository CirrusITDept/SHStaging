# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record:.value2 = float(record.value) / 100
# -*- coding: utf-8 -*-
# record.id

class SalesDashboardReportsOpsByDay(models.Model):
    _name = "dashboard.sales.opsbyday"
    _description = "Dashboard Opps By Day"
    #fields.Many2one("res.partner", string="Account Name")
    user_id  = fields.Many2one("res.users", string="SalesPerson")
   # user_id  = fields.Integer(string="Sales Person")
    Total     = fields.Integer(string="Total Opps")

class SalesDashboardReportsOpsForMonth(models.Model):
    _name = "dashboard.sales.opsformonth"
    _description = "Dashboard Opps for month"
    user_id  = fields.Many2one("res.users", string="SalesPerson")
    total    = fields.Integer(string="Total Opps")

class SalesDashboardReportsTotals(models.Model):
    _name = "dashboard.sales.singletotals"
    _description = "Dashboard Totals"
    ops_day_total      = fields.Integer(string="Total Daily Opps")
    ops_month_total    = fields.Integer(string="Total Monthly Opps")
    month__disp_total  = fields.Integer(string="Displays  Sold Month")
    ave_sales_rep      = fields.Integer(string="Average Sales Per Rep")
    Ave_Deal_Year      = fields.Integer(string="Average Deal size Year")



#This function is called when the scheduler goes off
@api.model
def process_demo_scheduler_queue(self):
         _logger.debug('Yo debug logger')


 



@api.model
class ProductTest(models.Model):
    _inherit = "product.product"
    def test_function(self):
        categories = self.env['product.category'].search([('id', '=', 5)]).ids
        return {
            'name': 'Accessories',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'domain': [('categ_id', 'in', categories)],
            'res_model': 'product.product',
            'target': 'current'
        }
    




def _get_last_sale(self):
#    return fields.datetime.now()   
#    kvar = self.date_lastsfpurch =  self.env["sale.order"].search(
    self.env["sale.order"].search(
        [
            ('partner_id','=', self.id),
            ('order', 'create_date', 'DESC'),
        ],
        limit = 1
    ).create_date
#    kvar = 0
#    return fields.Date.context_today
    


#class ResPartner(models.Model):
#    _inherit = 'res.partner'
#    date_lastsfpurch = fields.Date(
#    string="Salesforce Last Purchase",
#    store=True,
#    readonly=False,
#    default=_get_last_sale,
#    default=fields.Date.context_today,
#    )
   
