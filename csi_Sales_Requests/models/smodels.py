# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)



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
    



   
#-------------------------------- CRM Lead cal rev from SO's -----------------------------------------
class Crm_Lead_Average_Quote_total(models.Model):
    _inherit = 'crm.lead'

    ave_total_of_quotes = fields.Float(
        compute="_compute_average_quote_total", 
        string="Opp average quote total",
        default = 0.0,
    )
    computed_ave_quotes = fields.Float(
        string="Computed Ave of Quotes",
        default = 0.0,
    )

    def _compute_average_quote_total(self):
        for opp in self:
            opp.ave_total_of_quotes = 0
            #opp.computed_ave_quotes  = 0
            cnt   =  self.env["sale.order"].search_count( [("opportunity_id", "=", opp.id),("state", "!=", 'cancel')])
            Locked = False
            if(cnt):
                recs = self.env["sale.order"].search( [("opportunity_id", "=", opp.id),("state", "!=", 'cancel')])
                for so in recs:
                    if so.state == 'done':
                        Locked = True
                        #This opp has a win. computed = win total only
                        opp.ave_total_of_quotes  = so.amount_total
                        opp.computed_ave_quotes  = so.amount_total
                        continue   
                    elif Locked != True:
                        opp.ave_total_of_quotes = opp.ave_total_of_quotes + so.amount_total


                if(not Locked):    
                    opp.ave_total_of_quotes  = opp.ave_total_of_quotes / cnt
                    opp.computed_ave_quotes  = opp.ave_total_of_quotes
                else:
                    opp.ave_total_of_quotes = opp.computed_ave_quotes    
            else:
                opp.computed_ave_quotes= opp.ave_total_of_quotes
                continue    
         
#        return


