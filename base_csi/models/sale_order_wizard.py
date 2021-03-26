# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"
    _description = "Sale Order Wizard"

    order_id = fields.Many2one("sale.order", string="Sale Order")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", related="order_id.currency_id"
    )
    product_id = fields.Many2one("product.product", string="Product")
    product_price = fields.Float(
        string="Product Price", related="product_id.list_price"
    )
    height = fields.Integer(string="Height")
    width = fields.Integer(string="Width")
    panel_count = fields.Float(string="Panel Count", compute="_get_computed_values")
    panel_total = fields.Float(string="Panel Subtotal", compute="_get_computed_values")
    siding = fields.Selection(
        [("single", "Single-Sided"), ("double", "Double-Sided")], default="single"
    )
    controller_id = fields.Many2one("product.product", string="Controller")
    controller_price = fields.Float(
        string="Controller Price", related="controller_id.list_price"
    )
    power_injector_count = fields.Integer(
        string="Power Injector Count", comptute="_get_computed_values"
    )
    power_injector_id = fields.Many2one("product.product", string="Power Injector")
    power_injector_price = fields.Float(
        string="Power Injector Price", related="power_injector_id.list_price"
    )
    carrier_id = fields.Many2one("delivery.carrier", string="Shipping Method")
    carrier_cost = fields.Float(string="Carrier Cost")
    service_module_id = fields.Many2one("product.product", string="Service Module")
    service_cost = fields.Float(
        string="Service Price", related="service_module_id.list_price"
    )
    service_module_count = fields.Integer(string="Service Count")
    service_total = fields.Float(
        string="Service Subtotal", compute="_get_computed_values"
    )
    grand_total = fields.Float(string="Grand Total", compute="_get_computed_values")

    aluminum_frame = fields.Integer(string="Aluminum Frame")
    wifi_unit = fields.Boolean(string="Wifi Unit")
    optional_controller = fields.Integer(string="Optional Controller Count")
    led_panel = fields.Integer(string="LED Panel")
    extension_cable = fields.Integer(string="Extension Cable")
    aluminum_frame_id = fields.Many2one("product.product", string="Aluminum Frame ID")
    wifi_unit_id = fields.Many2one("product.product", string="Wifi Unit ID")
    led_panel_id = fields.Many2one("product.product", string="LED Panel ID")
    extension_cable_id = fields.Many2one("product.product", string="Extension Cable ID")
    aluminum_frame_price = fields.Float(
        string="Aluminum Frame Price", related="aluminum_frame_id.list_price"
    )
    wifi_unit_price = fields.Float(
        string="Wifi Unit Price", related="wifi_unit_id.list_price"
    )
    led_panel_price = fields.Float(
        string="LED Panel Price", related="led_panel_id.list_price"
    )
    extension_cable_price = fields.Float(
        string="Extension Cable Price", related="extension_cable_id.list_price"
    )
    addtl_total = fields.Float(string="Addtl. Subtotal", compute="_get_computed_values")
    height_warning = fields.Boolean(
        string="Height Warning", compute="_get_computed_values", store="True"
    )
    width_warning = fields.Boolean(
        string="Width Warning", compute="_get_computed_values", store="True"
    )

    # TODO Frame type logic
    # frame_type_a_count = fields.Integer(string="1' x 2' Frame Count", default=2)
    # frame_type_b_count = fields.Integer(string="2' x 4' Frame Count", default=2)

    def create_order_lines(self):
        for record in self:
            orderid = record.order_id.id
            line = record.env["sale.order.line"]

            # Panel Contents
            line.create(
                {
                    "order_id": orderid,
                    "name": "Panel Information",
                    "display_type": "line_section",
                }
            )
            if record.product_id:
                line.create(
                    {
                        "order_id": orderid,
                        "product_id": record.product_id.id,
                        "product_uom_qty": record.panel_count,
                    }
                )
            if record.power_injector_count > 0:
                line.create(
                    {
                        "order_id": orderid,
                        "product_id": record.power_injector_id.id,
                        "product_uom_qty": record.power_injector_count,
                    }
                )
            if record.controller_id:
                line.create(
                    {
                        "order_id": orderid,
                        "product_id": record.controller_id.id,
                        "product_uom_qty": record.optional_controller + 1,
                    }
                )

            # Addtl Items
            line.create(
                {
                    "order_id": orderid,
                    "name": "Additional Items",
                    "display_type": "line_section",
                }
            )
            if record.aluminum_frame_id and record.aluminum_frame > 0:
                line.create(
                    {
                        "order_id": orderid,
                        "product_id": record.aluminum_frame_id.id,
                        "product_uom_qty": record.aluminum_frame,
                    }
                )
            if record.wifi_unit and record.wifi_unit_id:
                line.create(
                    {
                        "order_id": orderid,
                        "product_id": record.wifi_unit_id.id,
                        "product_uom_qty": 1,
                    }
                )
            if record.led_panel_id and record.led_panel > 0:
                line.create(
                    {
                        "order_id": orderid,
                        "product_id": record.led_panel_id.id,
                        "product_uom_qty": record.led_panel,
                    }
                )
            if record.extension_cable_id and record.extension_cable > 0:
                line.create(
                    {
                        "order_id": orderid,
                        "product_id": record.extension_cable_id.id,
                        "product_uom_qty": record.extension_cable,
                    }
                )
            # Service contents
            line.create(
                {
                    "order_id": orderid,
                    "name": "service information",
                    "display_type": "line_section",
                }
            )
            if record.service_module_id:
                line.create(
                    {
                        "order_id": orderid,
                        "product_id": record.service_module_id.id,
                        "product_uom_qty": record.service_module_count,
                    }
                )
            if record.carrier_id:
                record.order_id.carrier_id = record.carrier_id
                if record.carrier_cost > 0:
                    record.order_id.delivery_price = record.carrier_cost
                    record.order_id.delivery_rating_success = True
                    record.order_id.set_delivery_line(
                        record.carrier_id, record.carrier_cost
                    )

    @api.depends(
        "height",
        "width",
        "product_id",
        "siding",
        "controller_id",
        "service_module_id",
        "service_module_count",
        "carrier_cost",
        "aluminum_frame",
        "wifi_unit",
        "led_panel",
        "extension_cable",
        "optional_controller",
    )
    def _get_computed_values(self):
        for record in self:
            record.height_warning = record.width_warning = False
            if record.product_id:
                prod_height = (
                    record.product_id.height if record.product_id.height else 1
                )
                prod_width = record.product_id.width if record.product_id.width else 1
                # Is the lenght of width divisible by the panel size
                if record.height > 0 and record.height % prod_height != 0:
                    record.height_warning = True
                if record.width > 0 and record.width % prod_width != 0:
                    record.width_warning = True
                panel_count = (record.height * record.width) / (
                    prod_height * prod_width
                )
                # Single vs. Double
                if record.siding == "double":
                    panel_count = panel_count * 2
                panel_total = record.product_id.list_price * panel_count
                if record.controller_id:
                    panel_total += record.controller_id.list_price
                power_injector_count = 0
                if panel_count > 18:
                    # TODO: Power Injector Count
                    power_injector_count = int(panel_count / 3)
                if record.power_injector_id:
                    panel_total += (
                        power_injector_count * record.power_injector_id.list_price
                    )
                if record.product_id.cellular:
                    panel_total += 650
                if record.height_warning or record.width_warning:
                    panel_total = 0
                    panel_count = 0
                    power_injector_count = 0
                record.power_injector_count = power_injector_count
                record.panel_count = panel_count
                record.panel_total = panel_total

                # Services
                service_total = record.carrier_cost
                if record.service_module_id:
                    service_total += (
                        record.service_module_id.list_price
                        * record.service_module_count
                    )
                record.service_total = service_total

                # Addtl Total
                addtl_total = 0
                if record.controller_id:
                    addtl_total += record.controller_price * record.optional_controller
                if record.aluminum_frame_id:
                    addtl_total += record.aluminum_frame_price * record.aluminum_frame
                if record.wifi_unit and record.wifi_unit_id:
                    addtl_total += record.wifi_unit_price
                if record.led_panel_id:
                    addtl_total += record.led_panel_price * record.led_panel
                if record.extension_cable_id:
                    addtl_total += record.extension_cable_price * record.extension_cable
                record.addtl_total = addtl_total
                record.grand_total = addtl_total + service_total + panel_total

    @api.model
    def default_get(self, fields):
        result = super(SaleOrderWizard, self).default_get(fields)
        if self._context.get("active_id"):
            order_id = self._context["active_id"]
            result["order_id"] = order_id

            order = self.env["sale.order"].browse(order_id)
            company = order.company_id
            if company.sale_controller_id:
                result["controller_id"] = company.sale_controller_id.id
            if company.sale_power_injector_id:
                result["power_injector_id"] = company.sale_power_injector_id.id
            if company.sale_carrier_id:
                result["carrier_id"] = company.sale_carrier_id.id
            if company.sale_service_module_id:
                result["service_module_id"] = company.sale_service_module_id.id
            if company.sale_extension_cable_id:
                result["extension_cable_id"] = company.sale_extension_cable_id.id
            if company.sale_wifi_unit_id:
                result["wifi_unit_id"] = company.sale_wifi_unit_id.id
            if company.sale_aluminum_frame_id:
                result["aluminum_frame_id"] = company.sale_aluminum_frame_id.id
            if company.sale_led_panel_id:
                result["led_panel_id"] = company.sale_led_panel_id.id
        return result

    def _get_total_cost(self):
        for record in self:
            total_num_modules = (record.width * record.height) / 2
            if record.siding == "double":
                total_num_modules = total_num_modules * 2
            record.total_module_count = total_num_modules
            record.total_module_cost = (
                total_num_modules * record.product_id.standard_price
            )
            if total_num_modules <= 18:
                record.power_injector = 0
            else:
                # TODO Logic for power injectors
                record.power_injector = total_num_modules / 2
