from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError

class Quant(models.Model):
    _inherit = "stock.quant"
    
    @api.constrains('quantity')
    def check_quantity(self):
        for quant in self:
            if float_compare(quant.quantity, 1, precision_rounding=quant.product_uom_id.rounding) > 0 and quant.lot_id and quant.product_id.tracking == 'serial':
                raise ValidationError(_('A serial number(%s) should only be linked to a single product.') % quant.lot_id.name)            