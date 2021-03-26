from odoo import api, fields, models, SUPERUSER_ID, _
from lxml import etree

class Picking(models.Model):
    _inherit = "stock.picking"

    custom_move_lines = fields.One2many('custom.stock.move', 'picking_id', string="Additional Products", copy=True)
    custom_quality_alert = fields.One2many('quality.alert', 'x_studio_return_order', string="Quality Alert")
    
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