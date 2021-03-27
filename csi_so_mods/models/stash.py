
class SalesOrder_Total_Fulfill_overide(models.Model):
    _inherit = 'sale.order'
    @api.model
    def action_confirm(self):
#        rec = super(SalesOrder_Total_Fulfill_overide, self).action_confirm()
        rec = super(SalesOrder_Total_Fulfill_overide, self).action_confirm()
        abc = 0
        return rec

    #@api.onchange("so_return_picking_id") 
    #def check_if_transfer_update_needed(self):
    #    raise UserError(
    #                "Boo2"
    #            )
    #    return          
    # 
    # 
    # 



class SalesOrder_Push_Return_To_Transfer(models.Model):
    _inherit = 'sale.order'
    #@api.onchange('state') 
#    @api.onchange('write_date') 
    @api.onchange('team_id') 
    def _transfer_update_needed(self):
#        if self.state != "done":
        aid         = self.id
        bill        = self.is_billable
        dispname    = self.display_name
        RtnOrder    = self.so_return_picking_id
        #this is billable. Return
        if bill:
            return
#        data_record = self.env["stock.picking"].search( [("origin", "=", aid)]) 
#        data_record = self.env["stock.picking"].search( [("origin", "=", dispname)]) 
        data_record = self.env["stock.picking"].search( [("sale_id", "=", dispname)]) 
        for record in data_record:
            if record.return_picking_id:
                return            
            if record.picking_type_code == "incoming":
                record.return_picking_id = self.so_return_picking_id 
                return               
        return                



class BTN_Ret_To_Tran(models.Model):
    _inherit = ['sale.order']


    def action_confirm(self):
       
#        if self.state != "done":
#        raise RuntimeError('Yo')
        super(BTN_Ret_To_Tran, self).action_confirm()
        aid         = self.id
        bill        = self.is_billable
        dispname    = self.display_name
        RtnOrder    = self.so_return_picking_id
        #this is billable. Return
        if bill:
            return
#        data_record = self.env["stock.picking"].search( [("origin", "=", aid)]) 
#        data_record = self.env["stock.picking"].search( [("origin", "=", dispname)]) 
        data_record = self.env["stock.picking"].search( [("sale_id", "=", dispname)]) 
        for record in data_record:
            if record.return_picking_id:
                return            
#            if record.location_id == "WH/Output":
            if record.picking_type_code == "incoming":
                record.return_picking_id = self.so_return_picking_id 
                return               
              