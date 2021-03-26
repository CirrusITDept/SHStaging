# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import re

#from odoo.osv import osv
#from odoo.tools.translate import _


# class csi_so_mods(models.Model): i
#     _name = 'csi_so_mods.csi_so_mods'
#     _description = 'csi_so_mods.csi_so_mods'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


class SalesOrder_Cirrus_Ref(models.Model):
    _inherit = 'sale.order'
    cirrus_ref = fields.Char(
    string="CirrusLED Reference",
    store=True,
    readonly=False,
    default=None,
    #    default=fields.Date.context_today,
    )

class SalesOrder_Is_Billable(models.Model):
    _inherit = 'sale.order'
    is_billable = fields.Boolean(
    string="Is Billable",
    store=True,
    readonly=False,
    default=True,
    )


 
class SalesOrder_So_Add_Return(models.Model):
    _inherit = 'sale.order'
    so_return_picking_id = fields.Many2one("stock.picking", string="Return Order")



class Display_Add_ControllerDetails(models.Model):
      _inherit = 'display.display'
      controller_details = fields.Html(
      string="Controller Details",
      store=True,
      readonly=False,
      default='',
      )

class SalesOrder_Total_ticket_Count(models.Model):
    _inherit = 'display.display'

    all_helpdesk_ticket_count = fields.Integer(
        compute="_compute_record_count_total", 
        string="Helpdesk Ticket Count Total"
    )

    def _compute_record_count_total(self):
        for display in self:
            display.all_helpdesk_ticket_count = self.env["helpdesk.ticket"].search_count(
                [("display_id", "=", display.id)]
            
            )

##Live one


class SO_Push_Ret_To_Tran(models.Model):
    _inherit = ['sale.order']

    def transfer_return_incomming(self):
       
#        aid         = self.id
        bill        = self.is_billable
        dispname    = self.display_name
#        RtnOrder    = self.so_return_picking_id
        #this is billable. Return
        if bill:
            return
        data_record = self.env["stock.picking"].search( [("sale_id", "=", dispname)]) 
        for record in data_record:
            #already had a return order assigned, return
            if record.return_picking_id:
                return            
            #find outgoing transfer and update return order
            if record.picking_type_code == "outgoing":
                record.return_picking_id = self.so_return_picking_id 
                return               
              






#Move Tracking from WH/OUT to WH/IN transfer order when 
#WH/OUT tracking is changed
#class SalesOrder_Return_Tracking_Transefer_WHIN(models.Model):
#    _inherit = 'stock.picking'
#    @api.onchange('return_carrier_tracking_ref')
#    def _onchange_return_tracking_ref(self):
#        if self.return_carrier_tracking_ref:
#            if self.return_picking_id:
#                Update_Rec = self.return_picking_id
#                if Update_Rec:
#                    Update_Rec.write({'carrier_tracking_ref': self.return_carrier_tracking_ref})


#----------------------------SO Ready for review - Fulfill----------------------------------------------------#
class SalesOrder_Is_Ready_For_Review(models.Model):
    _inherit = 'sale.order'
    ready_for_review = fields.Boolean(
    string="Ready for review",
    store=True,
    readonly=False,
    default=False,
    )


#---------------------------- Custom item picking alert from SO----------------------------------------------------#
class Sale_Order_Custom_Item_Alert(models.Model):
    _inherit = 'sale.order'

    custom_item_enable = fields.Boolean(
    string="Custom Item or Repair",
    help="Enabled: There is a custom item or repair attached to this SO",
    store=True,
    readonly=False,
    default=False,
  
    )


class SalesOrder_Picking_Custom_Item_Alert(models.Model):
    _inherit = 'stock.picking'

    rel_pick_custom_item_alert = fields.Boolean(
    related="sale_id.custom_item_enable",    
    string="Display Custom Item Alert",
    default=False,

    )




#----------------------------Display_Display_Alert_Enable----------------------------------------------------#

class Display_Display_Alert_Types_Table(models.Model):
    _name = "display.alert_types"
    _description = "Alert types for Display records"
    name = fields.Char(
        string="Alert Type",
        index=True
         )
    alert_note = fields.Html(
        string="Alert Notes",
        store=True,        
         )


class Display_Display_Add_Enable_Alert_Box(models.Model):
    _inherit = 'display.display'
    display_alert_enable = fields.Boolean(
    string="Enable Alert",
    help="Enabled: The Display has an alert tied to it",
    store=True,
    readonly=False,
    default=False,
    )

    m2o_display_alert_type = fields.Many2one(
    "display.alert_types",
    help="Define or select an Alert type. To enable place a check mark in the Enable Alert box",
    string="Alert Type"
    )
    


#---------------------------
class SalesOrder_Display_Add_Alert_Type(models.Model):
    _inherit = 'sale.order'
    so_rel_enable_display_alert = fields.Boolean(
    related="display_id.display_alert_enable",    
    string="Display Sales Alert",
    default=False,
    )
    m2o_sale_order_alert_type = fields.Many2one(
    related="display_id.m2o_display_alert_type",
    string = "Related Sales alert type"
    )


#---------------------------
class Ticket_Display_Add_Alert_Type(models.Model):
    _inherit = 'helpdesk.ticket'
    ticket_rel_enable_display_alert = fields.Boolean(
    related="display_id.display_alert_enable",    
    string="Display Ticket Alert",
    default=False,
    )
    m2o_ticket_alert_type = fields.Many2one(
    related="display_id.m2o_display_alert_type",
    string = "Related Ticket alert type"
    )
    

#---------------------------
class Quality_Display_Add_Alert(models.Model):
    _inherit = 'quality.alert'
    quality_rel_enable_alert = fields.Boolean(
    related="display_id.display_alert_enable",    
    string="Display Quality Alert",
    default=False,
    )
    m2o_quality_alert_type = fields.Many2one(
    related="display_id.m2o_display_alert_type",
    string = "Related Display alert type"
    )




#---------------------------- Third Party API Data ----------------------------------------------------#

class HelpDesk_Third_Party_API_Data_Exchange(models.Model):
    _name = "helpdesk.apiexchange"
    _description = "Data exchange from third parties"
    
    #hd_ticket_id
    #disposition_num
    #recording_url
    #client_phone
    #user_id
    #call_date
    
    name = fields.Char(
        string="Name",
        store=True,        
         )
    hd_ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Ticket ID",
        store=True,        
         )
    disposition_num = fields.Char(
        string="Disposition Num",
        store=True,        
         )
    recording_url = fields.Char(
        string="Recording URL",
        store=True,        
         )
    client_phone = fields.Char(
        string="Client Phone",
        store=True,        
         )
    hd_user_id = fields.Many2one(
        "res.users",
        string="HD User",
        store=True,        
         )
    hd_call_date =  fields.Date(
        string="Call date",
        store=True,        
         )



#---------------------------- FedEx Barcode Scannig ----------------------------------------------------#

def recognize_delivery_service(tracking):
    service = None
   
    usps_pattern = [
        '^(94|93|92|94|95)[0-9]{20}$',
        '^(94|93|92|94|95)[0-9]{22}$',
        '^(70|14|23|03)[0-9]{14}$',
        '^(M0|82)[0-9]{8}$',
        '^([A-Z]{2})[0-9]{9}([A-Z]{2})$'
    ]

    ups_pattern = [
        '^(1Z)[0-9A-Z]{16}$',
        '^(T)+[0-9A-Z]{10}$',
        '^[0-9]{9}$',
        '^[0-9]{26}$'
    ]
    
    fedex_pattern = [
        '^[0-9]{20}$',
        '^[0-9]{15}$',
        '^[0-9]{12}$',
        '^[0-9]{22}$'
    ]
    
    usps = "(" + ")|(".join(usps_pattern) + ")"
    fedex = "(" + ")|(".join(fedex_pattern) + ")"
    ups= "(" + ")|(".join(ups_pattern) + ")"
    
    if re.match(usps, tracking) != None:
        service = 'USPS'
    elif re.match(ups, tracking) != None:
        service = 'UPS'
    elif re.match(fedex, tracking) != None:
        service = 'FedEx'

    return service

class Stock_Picking_Return_Tracking_URL(models.Model):
    _inherit = 'stock.picking'
    x_csi_return_trk_url  = fields.Char(string="Tracking URL")
    x_csi_return_pick_url = fields.Char(string="Tracking URL")








#TEST Code#

class HelpDesk_Rating_Report_Mod(models.Model):
    _inherit = 'rating.rating'

    nps_vaule = fields.Integer(
        compute="_compute_rating_kpi_nps", 
        string="NPS value",
        store = True,
        index = True

    )

    def _compute_rating_kpi_nps(self):
        for rating in self:
            prenps = rating.rating
            if prenps:
                if prenps >= 9:
                    prenps = 100
                elif prenps >= 7 and prenps <= 8:
                    prenps = 0
                elif prenps <= 6:
                    prenps = -100

            rating.nps_vaule = prenps   

            
            





#--------------------------------------------------------------------------------#
#Move Tracking from WH/OUT to WH/IN transfer order when 
#WH/OUT tracking is changed
#class SalesOrder_Return_Tracking_Transefer_WHIN(models.Model):
#    _inherit = 'stock.picking'
#    @api.onchange('return_carrier_tracking_ref')
#    #Find WH/IN/record attached to this one.
#    #stock.picking->carrier_tracking_ref
#    def _onchange_return_tracking_ref(self):
#        if self.return_carrier_tracking_ref:
#            if self.return_picking_id:
#                Update_Rec = self.return_picking_id
#                if Update_Rec:
#                    #raise osv.except_osv(_('name'),_(Update_Rec))
#                    Update_Rec.write({'carrier_tracking_ref': self.return_carrier_tracking_ref})



#class SalesOrder_Return_Tracking_Transefer_OnConfirm(models.Model):
#    _inherit = 'sale.order'
#    @api.model
#    $def action_confirm(self,vals):
#        res = super(SalesOrder_Return_Tracking_Transefer_OnConfirm, self).action_confirm()
#        self.ensure_one()
#        RtnOrder = self.env["stock.picking"].search([("sale_id", "=", self.id)])
#        if RtnOrder:
#            print(RtnOrder)
#            RtnOrder[0].write(({'return_picking_id': self.so_return_picking_id}))
#        return res
