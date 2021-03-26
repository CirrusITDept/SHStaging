# -*- coding: utf-8 -*-


from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cellular = fields.Boolean(string="Cellular")
    controller = fields.Boolean(string="Controller")  # sale.order.wizard deprecation?
    height = fields.Float(string="Length (Ft.)")
    width = fields.Float(string="Width (Ft.)")
    module_type = fields.Selection(
        [
            ("BladeM", "BladeM"),
            ("BladeX", "BladeX"),
            ("solof", "Solo Fire"),
            ("soloi", "Solo Ice"),
        ],
        string="Module Type",
    )
    module_color = fields.Selection(
        [("rgb", "Full Color RGB"), ("bw", "Black & White")], string="Module Color"
    )
    module_pitch = fields.Selection(
        [("4mm", "4mm"), ("6mm", "6mm"), ("9mm", "9mm")], string="Pixel Pitch",
    )
    module_pixel = fields.Float(string="Pixels Per Foot")
    is_module = fields.Boolean(string="Module")
    is_frame = fields.Boolean(string="Frame")
    is_controller = fields.Boolean(string="Controller")
    is_booster = fields.Boolean(string="Booster")
    is_service_module = fields.Boolean(string="Service Module")
    is_wifi = fields.Boolean(string="Wifi Unit")
    delivery_length = fields.Float(string="Length")
    delivery_width = fields.Float(string="Width")
    delivery_height = fields.Float(string="Height")
    tariff_code = fields.Char(string="Tariff (HN) Code")
    country_origin = fields.Many2one("res.country", string="Country of Origin")
    service_module_id = fields.Many2one("product.product", string="Service Module")
    warranty_module_price = fields.Float(string="Warranty Module Base Price")
    warranty_controller_price = fields.Float(string="Warranty Controller Base Price")
    commission_type = fields.Selection(
        [("commission", "Commissionable"), ("non_commission", "Non Commissionable")],
        string="Commission Type",
    )
    pm_cost = fields.Float(string="PM Cost", digits="Product Price")

    @api.onchange("commission_type")
    def onchange_commission_type(self):
        if self.commission_type != "commission":
            self.update({"pm_cost": 0.00})


class ProductProduct(models.Model):
    _inherit = "product.product"

    cellular = fields.Boolean(
        string="Cellular",
        store=True,
        readonly=False,
        related="product_tmpl_id.cellular",
    )
    controller = fields.Boolean(  # sale.order.wizard deprecation?
        string="Controller",
        store=True,
        readonly=False,
        related="product_tmpl_id.controller",
    )
    height = fields.Float(
        string="Length (Ft.)",
        store=True,
        readonly=False,
        related="product_tmpl_id.height",
    )
    width = fields.Float(
        string="Width (Ft.)",
        store=True,
        readonly=False,
        related="product_tmpl_id.width",
    )
    module_type = fields.Selection(
        [
            ("BladeM", "BladeM"),
            ("BladeX", "BladeX"),
            ("solof", "Solo Fire"),
            ("soloi", "Solo Ice"),
        ],
        string="Module Type",
        related="product_tmpl_id.module_type",
        readonly=False,
        store=True,
    )
    module_color = fields.Selection(
        [("rgb", "Full Color RGB"), ("bw", "Black & White")],
        string="Module Color",
        related="product_tmpl_id.module_color",
        readonly=False,
        store=True,
    )
    module_pitch = fields.Selection(
        [("4mm", "4mm"), ("6mm", "6mm"), ("9mm", "9mm")],
        string="Pixel Pitch",
        related="product_tmpl_id.module_pitch",
        readonly=False,
        store=True,
    )
    module_pixel = fields.Float(
        string="Pixels Per Foot",
        related="product_tmpl_id.module_pixel",
        readonly=False,
        store=True,
    )
    is_module = fields.Boolean(
        string="Module", related="product_tmpl_id.is_module", readonly=False, store=True
    )
    is_frame = fields.Boolean(
        string="Frame", related="product_tmpl_id.is_frame", readonly=False, store=True
    )
    is_controller = fields.Boolean(
        string="Controller",
        related="product_tmpl_id.is_controller",
        readonly=False,
        store=True,
    )
    is_booster = fields.Boolean(
        string="Booster",
        related="product_tmpl_id.is_booster",
        readonly=False,
        store=True,
    )
    is_service_module = fields.Boolean(
        string="Service Module",
        related="product_tmpl_id.is_service_module",
        readonly=False,
        store=True,
    )
    is_wifi = fields.Boolean(
        string="Wifi Unit",
        related="product_tmpl_id.is_wifi",
        readonly=False,
        store=True,
    )
    delivery_length = fields.Float(
        string="Length",
        related="product_tmpl_id.delivery_length",
        readonly=False,
        store=True,
    )
    delivery_width = fields.Float(
        string="Width",
        related="product_tmpl_id.delivery_width",
        readonly=False,
        store=True,
    )
    delivery_height = fields.Float(
        string="Height",
        related="product_tmpl_id.delivery_height",
        readonly=False,
        store=True,
    )
    tariff_code = fields.Char(
        string="Tariff (HN) Code",
        related="product_tmpl_id.tariff_code",
        readonly=False,
        store=True,
    )

    @api.onchange("commission_type")
    def onchange_commission_type(self):
        if self.commission_type != "commission":
            self.update({"pm_cost": 0.00})
