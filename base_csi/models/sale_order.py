# -*- coding: utf-8 -*-

from datetime import datetime
import math
import base64
from odoo import api, fields, models, _
import json
import requests
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    downpayment_type = fields.Selection([("50", "50%"), ("100", "100%")])
    amount = fields.Float(
        "Down Payment Amount",
        store=True,
        readonly=False,
        digits="Account",
        compute="_set_amount",
    )

    @api.depends("downpayment_type")
    def _set_amount(self):
        for record in self:
            if record.downpayment_type == "50":
                record.amount = 50
            elif record.downpayment_type == "100":
                record.amount = 100
                sale_orders = self.env["sale.order"].browse(
                    self._context.get("active_ids", [])
                )
                sale_orders.write(
                    {
                        "payment_term_id": self.env.ref(
                            "account.account_payment_term_immediate"
                        ).id
                    }
                )
            else:
                record.amount = 0


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    credit_card_fee = fields.Boolean(string="Credit Card Fee Line")
    pm_cost = fields.Float(
        "PM Cost", related="product_id.pm_cost", digits="Product Price"
    )

    @api.depends("product_id")
    def _compute_product_updatable(self):
        for line in self:
            if line.is_delivery:
                line.product_updatable = False
            else:
                super(SaleOrderLine, line)._compute_product_updatable()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_received = fields.Boolean(string="Payment Received")
    projected_install_date = fields.Date(
        string="Projected Install Date", copy=False, store=True
    )
    ticket_id = fields.Many2one("helpdesk.ticket", string="Created from Ticket")
    ticket_ids = fields.One2many(
        "helpdesk.ticket", "sale_id", string="Helpdesk Tickets"
    )
    alert_ids = fields.One2many("quality.alert", "sale_id", string="Quality Alerts")
    request_ids = fields.One2many("sign.request", "sale_id", string="Sign Requests")
    ticket_count = fields.Integer(string="Ticket Count", compute="_get_record_counts")
    request_count = fields.Integer(string="Request Count", compute="_get_record_counts")
    alert_count = fields.Integer(string="Alert Count", compute="_get_record_counts")
    partner_end_id = fields.Many2one("res.partner", string="End User")
    partner_sign_id = fields.Many2one("res.partner", string="Sign Shop")
    partner_dist_id = fields.Many2one("res.partner", string="Distributor")
    display_id = fields.Many2one("display.display", string="Display")
    delivery_price = fields.Float(
        string="Shipping Subtotal", readonly=False, copy=False
    )
    module_id = fields.Many2one(
        "product.product",
        string="Module",
        default=lambda self: self.env.user.company_id.sale_module_id.id,
    )
    frame_id = fields.Many2one(
        "product.product",
        string="Aluminum Frame",
        default=lambda self: self.env.user.company_id.frame_id.id,
    )
    controller_id = fields.Many2one(
        "product.product",
        string="Controller",
        default=lambda self: self.env.user.company_id.controller_id.id,
    )
    booster_id = fields.Many2one(
        "product.product",
        string="Power Booster",
        default=lambda self: self.env.user.company_id.booster_id.id,
    )
    service_module_id = fields.Many2one(
        "product.product",
        string="Service Module",
        store=True,
        readonly=False,
        compute="_get_service_module",
    )
    wifi_id = fields.Many2one(
        "product.product",
        string="Wifi Unit",
        default=lambda self: self.env.user.company_id.wifi_id.id,
    )
    module_price = fields.Float(string="Module Price", related="module_id.list_price")
    controller_price = fields.Float(
        compute="_compute_warranty_cost", string="Controller Price"
    )
    booster_price = fields.Float(
        string="Power Booster Price", related="booster_id.list_price"
    )
    service_module_price = fields.Float(
        string="Service Module Price", related="service_module_id.list_price"
    )
    addtl_controller_price = fields.Float(
        compute="_compute_addtl_controller_price",
        string="Additional Controller Price",
        store=True,
    )
    wifi_price = fields.Float(string="Wifi Unit Price", related="wifi_id.list_price")
    discount_type = fields.Selection(
        [("Markup", "Markup"), ("Discount", "Discount")], string="Markup/Discount"
    )
    discount = fields.Float(string="Discount")
    module_price_discount = fields.Float(
        compute="compute_module_price_discount",
        string="Module Price w/ Discount",
        store=True,
    )
    height = fields.Integer(string="Height")
    width = fields.Integer(string="Width")
    sidedness = fields.Selection(
        [("ss", "Single-Sided"), ("ds", "Double-Sided")],
        string="Sidedness",
        default="ss",
    )
    total_weight = fields.Float(string="Total Weight", related="module_id.weight")

    panel_count = fields.Integer(
        string="Panel Count", store=True, compute="_compute_panel_count"
    )
    controller_count = fields.Integer(
        string="Controller Count", default=1, readonly=True
    )
    booster_count = fields.Integer(
        string="Power Booster Count",
        store=True,
        readonly=False,
        compute="_compute_booster_count",
    )
    service_module_count = fields.Integer(string="Service Module Count")
    addtl_controller_count = fields.Integer(string="Additional Controller Count")
    wifi_count = fields.Integer(string="Wifi Unit Count")

    additional_wifi_total = fields.Float(
        string="Addtl Wifi Total", store=True, compute="_compute_display_totals"
    )
    panel_subtotal = fields.Float(
        string="Panel Subtotal", store=True, compute="_compute_display_totals"
    )
    display_subtotal = fields.Float(
        string="Display Subtotal", store=True, compute="_compute_display_totals"
    )
    display_subtotal_discount = fields.Float(
        string="Display Subtotal w/ Discount",
        store=True,
        compute="_compute_display_totals",
    )
    display_grand_total = fields.Float(
        string="Grand Total", store=True, compute="_compute_display_totals"
    )
    monthly_subscription = fields.Float(
        string="Monthly Subscription", store=True, compute="_compute_display_totals"
    )
    down_payment = fields.Float(
        string="Down Payment", store=True, compute="_compute_display_totals"
    )
    subscription_total = fields.Float(
        string="Total price", store=True, compute="_compute_display_totals"
    )
    n_down_payment = fields.Float(
        string="Down Payment Nonstore", compute="_nonstore_compute_display_totals"
    )
    n_subscription_total = fields.Float(
        string="Total price Nonstore", compute="_nonstore_compute_display_totals"
    )
    face_area = fields.Float(
        string="Square Feet (per face)", store=True, compute="_compute_display_totals"
    )
    face_pixels = fields.Float(
        string="Pixels Per Face", store=True, compute="_compute_display_totals"
    )
    face_pixels_16mm = fields.Float(
        string="16mm Pixels Per Face", store=True, compute="_compute_display_totals"
    )
    pixel_price = fields.Float(
        string="Price Per Pixel", store=True, compute="_compute_display_totals"
    )
    display_dimensions = fields.Char(
        string="Display Dimensions", store=True, compute="_compute_display_totals"
    )
    viewing_area = fields.Char(
        string="Viewing Area", store=True, compute="_compute_display_totals"
    )
    display_matrix = fields.Char(
        string="Display Matrix", store=True, compute="_compute_display_totals"
    )
    total_weight = fields.Float(
        string="Total Weight", store=True, compute="_compute_display_totals"
    )
    avg_power = fields.Float(
        string="Average Continuous Power", store=True, compute="_compute_display_totals"
    )
    electrical_information = fields.Char(
        string="Electrical Information @", store=True, compute="_compute_display_totals"
    )
    max_current = fields.Float(
        string="Max Current", store=True, compute="_compute_display_totals"
    )
    input_voltage = fields.Char(
        string="Input Voltage", store=True, compute="_compute_display_totals"
    )
    addtl_power_inputs = fields.Char(
        string="Additional Power Inputs", store=True, compute="_compute_display_totals"
    )
    power_setup = fields.Text(
        string="Required Power Setup", store=True, compute="_compute_display_totals"
    )
    addtl_controller_cellular = fields.Char(
        string="Additional Controller Cellular", compute="_compute_display_totals"
    )
    is_cellular = fields.Boolean(
        string="Cellular", related="controller_id.cellular", readonly=True
    )
    # @Jay - Need to implement below field as per functionality, I add for SO report
    addtl_controller_total = fields.Float()
    wifi_total = fields.Float()
    booster_total = fields.Float()
    delivery_carrier_code = fields.Many2one(
        "delivery.shipstation.carrier",
        string="Carrier Code",
        related="carrier_id.carrier_code",
    )
    delivery_package = fields.Many2one(
        "delivery.shipstation.package", string="Delivery Package"
    )
    delivery_length = fields.Float(string="Length")
    delivery_width = fields.Float(string="Width")
    delivery_height = fields.Float(string="Height")
    client_account = fields.Many2one(
        "res.partner.shipping.account", string="Client Shipping Acct"
    )
    confirmation = fields.Selection(
        [
            ("none", "None"),
            ("delivery", "Delivery"),
            ("signature", "Signature"),
            ("adult_signature", "Adult Signature"),
            ("direct_signature", "Direct Signature"),
        ],
        string="Delivery Confirmation",
        default="none",
        copy=False,
    )
    all_shipped = fields.Boolean(
        string="All Shipped", store=True, compute="calc_all_shipped"
    )
    booster_total = fields.Float(
        string="Power Booster Total", store=True, compute="_compute_display_totals"
    )
    addtl_controller_total = fields.Float(
        string="Additional Controller Total",
        store=True,
        compute="_compute_display_totals",
    )
    wifi_total = fields.Float(
        string="Wifi Unit Total", store=True, compute="_compute_display_totals"
    )
    amount_total_minus_shipping = fields.Float(
        string="Total Minus Shipping", store=True, compute="_compute_display_totals"
    )
    n_amount_total_minus_shipping = fields.Float(
        string="Total Minus Shipping (Nonstore)",
        compute="_nonstore_compute_display_totals",
    )
    pixel_pitch = fields.Selection(
        [("4mm", "4mm"), ("6mm", "6mm"), ("9mm", "9mm")],
        string="Pixel Pitch",
        store=True,
        related="module_id.module_pitch",
    )
    warranty_cost = fields.Float(
        string="Warranty Monthly Cost", compute="_compute_warranty_cost"
    )
    warranty_cost_upfront = fields.Float(
        string="Warranty Cost Upfront", compute="_compute_warranty_cost"
    )
    override_warranty_cost = fields.Float(string="Override Warranty Monthly Cost")
    cirruscomplete_selection = fields.Selection(
        [
            ("cir_complete", "CirrusComplete = Service + Cellular Up Front"),
            ("cir_complete_month", "CirrusComplete Monthly"),
            ("cel_upfront", "Cellular Up Front"),
        ],
        string="Cirrus Complete",
    )
    sign_request = fields.Boolean(help="Technical field to add extra page in report")
    is_single_display_sale = fields.Boolean(string="Single Display Sale?", copy=True)
    x_so_profit_margin = fields.Float(
        string="Profit Margin",
        compute="_compute_profit_margin",
        digits="Product Price",
    )
    x_so_new_sign_shop = fields.Boolean(
        string="New Customer", related="partner_id.new_sign_shop"
    )
    commission_amount = fields.Float(
        string="Commission Amount", compute="compute_commission_amount", store=True
    )

    @api.depends("order_line.pm_cost", "order_line.product_uom_qty")
    def _compute_profit_margin(self):
        """calculates profit margin of the order.
        profit margin is the difference between the total price and pm_cost*qty of order lines with commisiionable products
        """
        for order in self:
            total_cost = 0
            commissionable_lines = order.order_line.filtered(
                lambda r: r.product_id.commission_type == "commission"
            )
            subtotal = sum(commissionable_lines.mapped("price_subtotal"))
            for line in commissionable_lines:
                total_cost += line.pm_cost * line.product_uom_qty
            order.x_so_profit_margin = subtotal - total_cost

    @api.depends(
        "opportunity_id.channel_type_id", "partner_id.new_sign_shop", "order_line"
    )
    def compute_commission_amount(self):
        for rec in self:
            rec.commission_ammount = 0.00
            if rec.opportunity_id:
                if rec.opportunity_id.channel_type_id == "sbm":
                    rec.commission_amount = rec.x_so_profit_margin * 0.065
                if (
                    rec.opportunity_id.channel_type_id != "sbm"
                    and rec.partner_id.new_sign_shop
                ):
                    rec.commission_amount = rec.x_so_profit_margin * 0.105
                if (
                    rec.opportunity_id.channel_type_id != "sbm"
                    and not rec.partner_id.new_sign_shop
                ):
                    rec.commission_amount = rec.x_so_profit_margin * 0.06

    def create_display(self):
        view_id = self.env.ref("base_csi.view_display_records_form").id
        cellular_paid = False
        sidedness = False
        if self.cirruscomplete_selection == "cir_complete":
            cellular_paid = True
        if self.cirruscomplete_selection == "cir_complete_month":
            cellular_paid = False
        if self.cirruscomplete_selection == "cel_upfront":
            cellular_paid = True
        if self.sidedness == "ss":
            sidedness = "One (1)"
        if self.sidedness == "ds":
            sidedness = "Two (2)"
        return {
            "name": _("Create Display"),
            "type": "ir.actions.act_window",
            "view_id": view_id,
            "view_mode": "form",
            "res_model": "display.display",
            "context": {
                "default_name": self.client_order_ref,
                "default_sign_shop_contact": self.partner_id.id,
                "default_sign_shop": self.partner_sign_id.id,
                "default_purchase_date": self.date_order,
                "default_projected_install_date": self.projected_install_date,
                "default_pitch": self.module_id.module_pitch,
                "default_height": self.height,
                "default_width": self.width,
                "default_number_of_faces": sidedness,
                "default_display_matrix": self.display_matrix,
                "default_end_user_contact": self.partner_end_id.id,
                "default_account": self.partner_end_id.commercial_partner_id.id,
                "default_won_sale_id": self.id,
                "default_opportunity": self.opportunity_id.id,
                "default_cellular_paid": cellular_paid,
            },
        }

    @api.depends("discount_type", "discount", "module_price")
    def compute_module_price_discount(self):
        for rec in self:
            module_price_discount = 0.00
            if rec.discount_type:
                if rec.discount_type == "Discount":
                    module_price_discount = rec.module_price * (
                        1 - (rec.discount / 100)
                    )
                elif rec.discount_type == "Markup":
                    module_price_discount = rec.module_price * (
                        1 + (rec.discount / 100)
                    )
            elif rec.module_id.list_price:
                module_price_discount = rec.module_id.list_price
            rec.module_price_discount = module_price_discount

    @api.depends("module_id")
    def _get_service_module(self):
        for record in self:
            if record.module_id:
                record.service_module_id = record.module_id.service_module_id
            else:
                record.service_module_id = False

    def add_credit_card_fee(self):
        for record in self:
            product_line = record.company_id.credit_charge_product_id
            if not product_line:
                raise UserError(
                    "The company does not have a credit card charge product configured."
                )
            record.order_line.filtered(lambda b: b.credit_card_fee).unlink()
            amount_line = record.amount_total * (
                record.company_id.credit_charge_fee / 100
            )
            new_line = record.env["sale.order.line"].new(
                {
                    "product_id": product_line.id,
                    "price_unit": amount_line,
                    "credit_card_fee": True,
                }
            )
            record.order_line += new_line

    @api.depends("state", "order_line.product_uom_qty", "order_line.qty_delivered")
    def calc_all_shipped(self):
        for record in self:
            record.all_shipped = False
            if all(
                l.qty_delivered == l.product_uom_qty
                for l in record.order_line.filtered(
                    lambda x: x.product_id.type in ["consu", "product"]
                )
            ):
                record.all_shipped = True

    @api.onchange("delivery_package")
    def set_dimensions_on_change(self):
        for record in self:
            length = width = height = 0
            if record.delivery_package:
                length = record.delivery_package.delivery_length
                width = record.delivery_package.delivery_width
                height = record.delivery_package.delivery_height
            record.delivery_length = length
            record.delivery_width = width
            record.delivery_height = height

    @api.onchange("partner_id")
    def onchange_account_partner(self):
        for record in self:
            record.client_account = False
            record.set_customer_shipping_account()

    def set_customer_shipping_account(self):
        for record in self:
            if record.partner_id and record.partner_id.shipping_account_ids:
                shipping_account = record.partner_id.shipping_account_ids[0]
                record.client_account = shipping_account

    @api.onchange("client_account")
    def _filter_carriers(self):
        if self.client_account:
            action = {
                "domain": {
                    "carrier_id": [
                        ("carrier_code", "=", self.client_account.carrier_id.id)
                    ]
                }
            }
            return action
        else:
            action = {"domain": {"carrier_id": []}}
            return action
    
    def get_shipstation_rates(self):
        for record in self:
            wiz_id = record.env["sale.order.rate.wizard"].create(
                {"order_id": record.id}
            )
            if self.user_has_groups(
                "sales_team.group_sale_manager"
            ) or self.user_has_groups("base_csi.group_addtl_carrier"):
                rule_delivery_ids = record.env["delivery.carrier"].search(
                    [("delivery_type", "=", "base_on_rule")]
                )
            else:
                rule_delivery_ids = record.env["delivery.carrier"].search(
                    [
                        ("non_manager_display", "=", True),
                        ("delivery_type", "=", "base_on_rule"),
                    ]
                )
            new_lines = record.env["sale.order.rate.wizard.line"]
            for rule in rule_delivery_ids:
                carrier = rule._match_address(record.partner_shipping_id)
                if not carrier:
                    continue
                vals = rule.rate_shipment(record)
                display_price = 0
                if vals.get("success"):
                    display_price = vals["carrier_price"]
                    data = {
                        "wizard_id": wiz_id.id,
                        "valid": True,
                        "carrier_id": rule.id or False,
                        "carrier_code": "",
                        "service_code": "Rules Based",
                        "service_name": rule.name,
                        "rate": display_price,
                        "loaded_rate": display_price,
                        "other_cost": 0,
                    }
                    new_line = new_lines.create(data)
                    new_lines += new_line
            company = record.env.user.company_id
            if company.shipstation_key and company.shipstation_secret:
                # Retrieving Carriers
                carrier_url = "%s/carriers" % (company.shipstation_root_endpoint)
                conn = company.shipstation_connection(carrier_url, "GET", False)
                response = conn[0]
                content = conn[1]
                if response.status_code != requests.codes.ok:
                    raise UserError(
                        _("%s\n%s: %s" % (carrier_url, response.status_code, content))
                    )
                json_object_str = content.decode("utf-8")
                json_object = json.loads(json_object_str)
                order_weight = 0
                package_price = 0
                if record.delivery_package:
                    order_weight += record.delivery_package.package_weight
                    package_price += record.delivery_package.price
                for l in record.order_line:
                    if l.product_id.type in ["product", "consu"]:
                        order_weight += l.product_id.weight * l.product_uom_qty

                for c in json_object:
                    try:
                        url = "%s/shipments/getrates" % (
                            company.shipstation_root_endpoint
                        )
                        python_dict = {
                            "carrierCode": c["code"],
                            "fromPostalCode": company.zip,
                            "toState": record.partner_shipping_id.state_id.code,
                            "toCountry": record.partner_shipping_id.country_id.code,
                            "toPostalCode": record.partner_shipping_id.zip,
                            "toCity": record.partner_shipping_id.city,
                            "residential": record.partner_shipping_id.residential,
                            "confirmation": record.confirmation or False,
                            "weight": {"value": order_weight, "units": "ounces"},
                        }
                        if (
                            record.delivery_package
                            and record.delivery_package.created_by_shipstation
                        ):
                            python_dict.update(
                                {"packageCode": record.delivery_package.code}
                            )
                            if (
                                record.delivery_length > 0
                                and record.delivery_width > 0
                                and record.delivery_height > 0
                            ):
                                python_dict.update(
                                    {
                                        "dimensions": {
                                            "units": "inches",
                                            "length": int(record.delivery_length),
                                            "width": int(record.delivery_width),
                                            "height": int(record.delivery_height),
                                        }
                                    }
                                )
                        if (
                            record.delivery_package
                            and not record.delivery_package.created_by_shipstation
                        ):
                            python_dict.update({"packageCode": "package"})
                            python_dict.update(
                                {
                                    "dimensions": {
                                        "units": "inches",
                                        "length": int(
                                            record.delivery_package.delivery_length
                                        ),
                                        "width": int(
                                            record.delivery_package.delivery_width
                                        ),
                                        "height": int(
                                            record.delivery_package.delivery_height
                                        ),
                                    }
                                }
                            )
                        if (
                            not record.delivery_package
                            and record.delivery_length > 0
                            and record.delivery_width > 0
                            and record.delivery_height > 0
                        ):
                            python_dict.update(
                                {
                                    "dimensions": {
                                        "units": "inches",
                                        "length": int(record.delivery_length),
                                        "width": int(record.delivery_width),
                                        "height": int(record.delivery_height),
                                    }
                                }
                            )
                        data_to_post = json.dumps(python_dict)
                        conn = company.shipstation_connection(url, "POST", data_to_post)
                        response = conn[0]
                        content = conn[1]
                        if response.status_code != requests.codes.ok:
                            raise UserError(
                                _("%s\n%s: %s" % (url, response.status_code, content))
                            )
                        json_object_str = content.decode("utf-8")
                        json_object = json.loads(json_object_str)
                        if len(json_object) > 0:
                            for rate in json_object:
                                if self.user_has_groups(
                                    "sales_team.group_sale_manager"
                                ) or self.user_has_groups(
                                    "base_csi.group_addtl_carrier"
                                ):
                                    delivery_id = record.env["delivery.carrier"].search(
                                        [("service_code", "=", rate["serviceCode"])],
                                        limit=1,
                                    )
                                else:
                                    delivery_id = record.env["delivery.carrier"].search(
                                        [
                                            ("non_manager_display", "=", True),
                                            ("service_code", "=", rate["serviceCode"]),
                                        ],
                                        limit=1,
                                    )
                                if delivery_id:
                                    loaded_rate = (
                                        rate["shipmentCost"] + rate["otherCost"]
                                    ) * (1 + (delivery_id.margin / 100)) + package_price
                                    data = {
                                        "wizard_id": wiz_id.id,
                                        "valid": True,
                                        "carrier_id": delivery_id.id or False,
                                        "carrier_code": c["code"],
                                        "service_code": rate["serviceCode"],
                                        "service_name": rate["serviceName"],
                                        "rate": rate["shipmentCost"]
                                        + rate["otherCost"],
                                        "loaded_rate": loaded_rate,
                                        "other_cost": rate["otherCost"],
                                    }
                                    new_line = new_lines.create(data)
                                    new_lines += new_line
                    except Exception as E:
                        print(E)
                        continue
            wiz_id.wizard_line_ids += new_lines
            action_data = record.env.ref(
                "base_csi.action_sale_order_rate_wizard"
            ).read()[0]
            action_data.update({"res_id": wiz_id.id})
            return action_data

    def _get_record_counts(self):
        for record in self.sudo():
            tickets = record.ticket_id
            tickets |= record.ticket_ids
            record.ticket_count = len(tickets)
            record.alert_count = len(record.alert_ids)
            record.request_count = len(record.request_ids)

    def button_quality_alert(self):
        self.ensure_one()
        action = self.env.ref("quality_control.quality_alert_action_check").read()[0]
        action["views"] = [(False, "form")]
        action["context"] = {
            "default_sale_id": self.id,
            "default_display_id": self.display_id.id,
        }
        return action

    def open_quality_alert(self):
        self.ensure_one()
        action = self.env.ref("quality_control.quality_alert_action_check").read()[0]
        action["context"] = {"default_sale_id": self.id}
        action["domain"] = [("id", "in", self.alert_ids.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if self.alert_count == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = self.alert_ids.id
        return action

    def open_sign_request(self):
        self.ensure_one()
        action = self.env.ref("sign.sign_request_action").read()[0]
        action["context"] = {"default_sale_id": self.id}
        action["domain"] = [("id", "in", self.request_ids.ids)]
        action["views"] = [(False, "kanban"), (False, "form")]
        if self.request_count == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = self.request_ids.id
        return action

    def open_ticket(self):
        self.ensure_one()
        action = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[0]
        action["context"] = {"default_sale_id": self.id}
        tickets = self.ticket_id
        tickets |= self.ticket_ids
        action["domain"] = [("id", "in", tickets.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if self.ticket_count == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = tickets.id
        return action

    def create_order_lines(self):
        for record in self.filtered(
            lambda b: b.state not in ["sale", "done", "cancel"]
        ):
            orderid = record.id
            record.order_line.unlink()
            line = record.env["sale.order.line"]
            line_list = []

            # Panel Contents
            line_list.append(
                {"order_id": orderid, "name": "Display", "display_type": "line_section"}
            )
            if record.module_id:
                line_list.append(
                    {
                        "order_id": orderid,
                        "product_id": record.module_id.id,
                        "product_uom_qty": record.panel_count,
                        "price_unit": record.module_price_discount
                        or record.module_price,
                    }
                )
            if record.frame_id:
                line_list.append(
                    {
                        "order_id": orderid,
                        "product_id": record.frame_id.id,
                        "product_uom_qty": record.panel_count,
                    }
                )
            if record.controller_id:
                line_list.append(
                    {
                        "order_id": orderid,
                        "product_id": record.controller_id.id,
                        "product_uom_qty": record.controller_count
                        + record.addtl_controller_count,
                        "price_unit": (
                            (record.controller_count * record.controller_price)
                            + (
                                record.addtl_controller_count
                                * record.addtl_controller_price
                            )
                        )
                        / (record.controller_count + record.addtl_controller_count),
                    }
                )
            if record.booster_id:
                line_list.append(
                    {
                        "order_id": orderid,
                        "product_id": record.booster_id.id,
                        "product_uom_qty": record.booster_count,
                    }
                )
            # Addtl Items
            line_list.append(
                {
                    "order_id": orderid,
                    "name": "Additional Items",
                    "display_type": "line_section",
                }
            )
            if record.service_module_id:
                line_list.append(
                    {
                        "order_id": orderid,
                        "product_id": record.service_module_id.id,
                        "product_uom_qty": record.service_module_count,
                    }
                )
            if record.wifi_id and record.wifi_count > 0:
                line_list.append(
                    {
                        "order_id": orderid,
                        "product_id": record.wifi_id.id,
                        "product_uom_qty": record.wifi_count,
                    }
                )
            # Service contents
            line_list.append(
                {
                    "order_id": orderid,
                    "name": "Shipping",
                    "display_type": "line_section",
                }
            )
            record.is_single_display_sale = True
            record.require_signature = False
            line.create(line_list)

    @api.onchange("is_single_display_sale")
    def onchnage_is_single_display_sale(self):
        if self.is_single_display_sale:
            self.require_signature = False

    def _nonstore_compute_display_totals(self):
        for record in self:
            delivery_line_total = 0
            amount_total_minus_shipping = record.amount_total
            if record.order_line.filtered(lambda b: b.is_delivery):
                delivery_line_total = sum(
                    record.order_line.filtered(lambda b: b.is_delivery).mapped(
                        "price_total"
                    )
                )
                amount_total_minus_shipping = record.amount_total - delivery_line_total
            down_payment = amount_total_minus_shipping * 0.15
            subscription_total = down_payment + record.delivery_price
            record.n_down_payment = down_payment
            record.n_subscription_total = subscription_total
            record.n_amount_total_minus_shipping = amount_total_minus_shipping
    
    def line_and_booster_cal(self, panel_count, module_id):
        booster_208 = booster_240 = 0
        if module_id.custom_208v > 0:
            booster_208 = int((panel_count - 1) / module_id.custom_208v)
        if module_id.custom_240v > 0:
            booster_240 = int((panel_count - 1) / module_id.custom_240v)
        
        line_240 = booster_240 + 1
        line_208 = booster_208 + 1
        return line_208, booster_208, line_240, booster_240
    
    def recalculate_power_values(self):
        for record in self:
            avg_power, electrical_information, input_voltage, max_current, power_setup = record.calculate_power_values()
            
            record.avg_power = avg_power
            record.electrical_information = electrical_information
            record.input_voltage = input_voltage
            record.max_current = max_current
            record.power_setup = power_setup
    
    def _recalculate_power_values_cron(self):
        sale_orders_obj = self.env["sale.order"]
        sale_orders = sale_orders_obj.search([("state", "in", ["draft", "sent"])])
        for record in sale_orders:
            avg_power, electrical_information, input_voltage, max_current, power_setup = record.calculate_power_values()
            
            #record.avg_power = avg_power
            #record.electrical_information = electrical_information
            #record.input_voltage = input_voltage
            #record.max_current = max_current
            #record.power_setup = power_setup
            
            self._cr.execute("""UPDATE sale_order set avg_power=%s, electrical_information=%s, input_voltage=%s, max_current=%s, power_setup=%s WHERE id = %s """,(
            avg_power, electrical_information, input_voltage, max_current, power_setup, record.id))
    
    def calculate_power_values(self):
        first_line_top = first_line_bottom = avg_power = 0
        
        if self.pixel_pitch == "9mm":
            if self.panel_count <= self.module_id.custom_120v:
                first_line_top = 1
                first_line_bottom = 0
        elif self.pixel_pitch == "6mm":
            if self.panel_count <= self.module_id.custom_120v:
                first_line = self.panel_count // 16
                first_line_top = first_line + 1
                first_line_bottom = (
                    first_line_top - 1 if (first_line_top - 1) >= 0 else 0
                )
        elif self.pixel_pitch == "4mm":
            if self.panel_count <= self.module_id.custom_120v:
                first_line = self.panel_count // 14
                first_line_top = first_line + 1
                first_line_bottom = (
                    int(first_line_top - 1) if (first_line_top - 1) >= 0 else 0
                )
                
        if self.pixel_pitch:
            avg_power = round(self.panel_count * self.module_id.custom_wattage + 100, 2)
            electrical_information = input_voltage = max_current = power_setup = False
            if self.panel_count > self.module_id.custom_120v:
                electrical_information = "240V"
                input_voltage = "208V-240V"
                max_current = round(avg_power / 240, 2)
                
                line_208, booster_208, line_240, booster_240 = self.line_and_booster_cal(self.panel_count, self.module_id)
                power_setup = """
                    208V: %s Lines of Power at 20 Amps - One line of power into the controller and %s into the boosters\n
                    240V: %s Lines of Power at 20 Amps - One line of power into the controller and %s into the boosters""" % (
                        line_208,
                        booster_208,
                        line_240,
                        booster_240,
                    )
            else:
                electrical_information = "120V"
                input_voltage = "120V-240V"
                max_current = round(avg_power / 120, 2)
                
                power_setup = """
                    120V: %s Lines of Power at 20 Amps - One line of power into the controller and %s into the boosters""" % (
                    first_line_top,
                    first_line_bottom,
                )
        
        return avg_power, electrical_information, input_voltage, max_current, power_setup
    
    @api.depends(
        "panel_count",
        "booster_count",
        "controller_count",
        "addtl_controller_count",
        "service_module_count",
        "wifi_count",
        "delivery_price",
        "discount",
        "discount_type",
        "height",
        "width",
        "module_id",
        "controller_id",
        "service_module_id",
    )
    def _compute_display_totals(self):
        for record in self:
            panel_count = record.panel_count
            panel_subtotal = panel_count * record.module_price
            record.booster_total = record.booster_count * record.booster_price
            record.addtl_controller_total = (
                record.addtl_controller_count * record.addtl_controller_price
            )
            record.wifi_total = (record.wifi_count) * record.wifi_price
            record.additional_wifi_total = (record.wifi_count) * record.wifi_price
            delivery_line_total = 0
            if record.order_line.filtered(lambda b: b.is_delivery):
                delivery_line_total = sum(
                    record.order_line.filtered(lambda b: b.is_delivery).mapped(
                        "price_total"
                    )
                )
            record.amount_total_minus_shipping = (
                record.amount_total - delivery_line_total
            )
            display_subtotal = sum(
                [
                    panel_subtotal,
                    (record.controller_count * record.controller_price)
                    + (record.addtl_controller_count * record.addtl_controller_price),
                    record.booster_count * record.booster_price,
                    record.service_module_count * record.service_module_price,
                    (record.wifi_count) * record.wifi_price,
                ]
            )
            display_subtotal_discount = display_subtotal
            if record.discount_type == "Markup":
                display_subtotal_discount = display_subtotal + (
                    panel_subtotal * (record.discount / 100)
                )
            elif record.discount_type == "Discount":
                display_subtotal_discount = display_subtotal - (
                    panel_subtotal * (record.discount / 100)
                )
            display_grand_total = record.delivery_price + display_subtotal_discount
            if record.module_id.module_pitch == "9mm":
                monthly_subscription = ((800 * panel_count) + 2350) / 60
            elif record.module_id.module_pitch == "6mm":
                monthly_subscription = ((1100 * panel_count) + 2350) / 60
            elif record.module_id.module_pitch == "4mm":
                monthly_subscription = ((1400 * panel_count) + 2350) / 60
            else:
                monthly_subscription = 0
            down_payment = 0
            subscription_total = down_payment + record.delivery_price

            module_pixel = record.module_id.module_pixel
            face_area = record.height * record.width
            record.face_area = face_area
            face_pixels = int(module_pixel * module_pixel * face_area)
            record.face_pixels = face_pixels
            record.face_pixels_16mm = int(face_area * 324)
            pixel_price = 0
            if face_pixels > 0:
                pixel_price = display_subtotal / face_pixels
                if record.sidedness == "ds":
                    pixel_price = display_subtotal / (face_pixels * 2)
            record.pixel_price = pixel_price
            dimensions = "%s feet tall x %s feet wide" % (record.height, record.width)
            record.viewing_area = dimensions
            record.display_dimensions = dimensions
            record.display_matrix = "%sx%s" % (
                int(record.height * module_pixel),
                int(record.width * module_pixel),
            )
            record.total_weight = round(record.module_id.weight * panel_count, 2)
            addtl_controller_cellular = ""
            if record.is_cellular:
                addtl_controller_cellular = ", with cellular"
            record.addtl_controller_cellular = addtl_controller_cellular
            
            electrical_information = max_current = input_voltage = power_setup = False
                        
            avg_power, electrical_information, input_voltage, max_current, power_setup = record.calculate_power_values()
            
            record.avg_power = avg_power
            record.electrical_information = electrical_information
            record.input_voltage = input_voltage
            record.max_current = max_current
            record.power_setup = power_setup
            record.addtl_power_inputs = "%s Power Boosters" % (record.booster_count)

            record.panel_subtotal = panel_subtotal
            record.display_subtotal = display_subtotal
            record.display_subtotal_discount = display_subtotal_discount
            record.display_grand_total = display_grand_total
            record.monthly_subscription = monthly_subscription
            record.down_payment = down_payment
            record.subscription_total = subscription_total

    def _compute_warranty_cost(self):
        for record in self:
            panel_count = record.panel_count
            warranty_cost = 0.0
            controller_price = 0.0
            if panel_count <= 31:
                warranty_cost = (panel_count * 1.25) + 12
            elif panel_count <= 39:
                warranty_cost = (panel_count * 1.15) + 12
            elif panel_count <= 99:
                warranty_cost = (panel_count * 1) + 12
            else:
                warranty_cost = (panel_count * 0.75) + 12
            record.warranty_cost = warranty_cost
            record.warranty_cost_upfront = warranty_cost * 60
            if (
                not record.cirruscomplete_selection
                or record.cirruscomplete_selection == "cir_complete_month"
            ):
                controller_price = record.controller_id.list_price
            elif record.cirruscomplete_selection == "cir_complete":
                controller_price = (
                    record.controller_id.list_price + record.warranty_cost_upfront
                )
            elif record.cirruscomplete_selection == "cel_upfront":
                if record.partner_id.country_id.code == "CA":
                    controller_price = record.controller_id.list_price
                else:
                    controller_price = record.controller_id.list_price
            record.controller_price = controller_price

    @api.onchange("width")
    def _check_multiple_of_two(self):
        for record in self:
            warning = False
            if record.width > 0 and record.width % 2 != 0:
                warning = {
                    "title": _("Incorrect input of %s for width") % record.width,
                    "message": "Width must be a multiple of 2.",
                }
                record.width = 0
        res = {}
        if warning:
            res["warning"] = warning
        return res

    @api.depends("pixel_pitch", "panel_count")
    def _compute_booster_count(self):
        for record in self:
            count = 0
            if record.panel_count > 0:
                if record.pixel_pitch == "9mm":
                    count = int(math.floor(record.panel_count / 36))
                    if record.panel_count % 36 == 0:
                        count -= 1
                elif record.pixel_pitch == "6mm":
                    count = int(math.floor(record.panel_count / 32))
                    if record.panel_count % 32 == 0:
                        count -= 1
                elif record.pixel_pitch == "4mm":
                    count = int(math.floor(record.panel_count / 30))
                    if record.panel_count % 30 == 0:
                        count -= 1
            record.booster_count = count

    @api.depends("sidedness", "height", "width")
    def _compute_panel_count(self):
        for record in self:
            if record.sidedness == "ds":
                record.panel_count = record.height * record.width
            else:
                record.panel_count = (record.height * record.width) / 2

    def open_sale_wizard(self):
        for record in self:
            action = self.env.ref("base_csi.action_window_sale_order_wizard")
            result = action.read()[0]
            return result

    @api.constrains("opportunity_id")
    def set_client_order_ref(self):
        for record in self:
            if record.opportunity_id:
                record.client_order_ref = record.opportunity_id.name

    def print_cirrus_quotation(self):
        self.filtered(lambda s: s.state == "draft").write({"state": "sent"})
        return self.env.ref("base_csi.action_report_cirrus_saleorder").report_action(
            self
        )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if not self.payment_term_id:
            self.payment_term_id = self.env.user.company_id.sale_payment_term_id

    def send_cirrus_quotation(self):
        orders = self.sudo()
        for record in orders:
            record.sign_request = True
            base_64_data = (
                record.env.ref("base_csi.action_report_cirrus_saleorder")
                .sudo()
                .render_qweb_pdf(record.ids)
            )
            report_picking_encode = base64.encodestring(base_64_data[0])
            name = "%s_%s_Cirrus_Quotation.pdf" % (
                record.name,
                datetime.now().strftime("%m-%d-%Y"),
            )
            attachment = record.env["ir.attachment"].create(
                {
                    "name": name,
                    "store_fname": name,
                    "datas": report_picking_encode,
                    "res_model": "sale.order",
                    "res_id": record.id,
                    "type": "binary",
                    "url": "url",
                    "mimetype": "application/pdf",
                }
            )
            template = (
                record.env["sign.template"]
                .sudo()
                .create({"sale_id": record.id, "attachment_id": attachment.id})
            )
            
            diff = 0
            if (record.pixel_pitch == '9mm' and record.panel_count <= 18 ) or ( record.pixel_pitch == '6mm' and record.panel_count <= 16 ) or ( record.pixel_pitch == '4mm' and record.panel_count <= 14 ):
                diff = 0.037
            
            if diff > 0:
                #120 V One line
                record.env["sign.item"].sudo().create(
                    [
                        {
                            "name": record.env.ref("sign.sign_item_type_signature").name,
                            "type_id": record.env.ref("sign.sign_item_type_signature").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 3,
                            "posX": 0.120,
                            "posY": 0.889,
                            "width": 0.154,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": record.env.ref("sign.sign_item_type_date").name,
                            "type_id": record.env.ref("sign.sign_item_type_date").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 3,
                            "posX": 0.321,
                            "posY": 0.889,
                            "width": 0.149,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Location name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.293 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                            "contact_info_type": "busi_name",
                        },
                        {
                            "name": "First name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.323 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                            "contact_info_type": "cont_name",
                        },
                        {
                            "name": "Last name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.353 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                            "contact_info_type": "last_name",
                        },
                        {
                            "name": "End User Email",
                            "type_id": record.env.ref("sign.sign_item_type_email").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.383 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                            "contact_info_type": "cont_email",
                        },
                        {
                            "name": "Initial",
                            "type_id": record.env.ref("sign.sign_item_type_initial").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.046,
                            "posY": 0.153,
                            "width": 0.080,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Initials",
                            "type_id": record.env.ref("sign.sign_item_type_initial").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.046,
                            "posY": 0.422 - diff,
                            "width": 0.080,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Business name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.608 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.637 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": record.env.ref("sign.sign_item_type_phone").name,
                            "type_id": record.env.ref("sign.sign_item_type_phone").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.666 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Email",
                            "type_id": record.env.ref("sign.sign_item_type_email").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.696 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact address",
                            "type_id": record.env.ref(
                                "sign.sign_item_type_multiline_text"
                            ).id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.726 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact city",
                            "type_id": record.env.ref("sign.sign_item_type_text").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.757 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact state",
                            "type_id": record.env.ref("sign.sign_item_type_text").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.786 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact zip",
                            "type_id": record.env.ref("sign.sign_item_type_text").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.815 - diff,
                            "width": 0.429,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact country",
                            "type_id": record.env.ref("sign.sign_item_type_text").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.845 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                    ]
                )
            else:
                record.env["sign.item"].sudo().create(
                    [
                        {
                            "name": record.env.ref("sign.sign_item_type_signature").name,
                            "type_id": record.env.ref("sign.sign_item_type_signature").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 3,
                            "posX": 0.120,
                            "posY": 0.889,
                            "width": 0.154,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": record.env.ref("sign.sign_item_type_date").name,
                            "type_id": record.env.ref("sign.sign_item_type_date").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 3,
                            "posX": 0.321,
                            "posY": 0.889,
                            "width": 0.149,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Location name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.291 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                            "contact_info_type": "busi_name",
                        },
                        {
                            "name": "First name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.321 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                            "contact_info_type": "cont_name",
                        },
                        {
                            "name": "Last name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.350 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                            "contact_info_type": "last_name",
                        },
                        {
                            "name": "End User Email",
                            "type_id": record.env.ref("sign.sign_item_type_email").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.380 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                            "contact_info_type": "cont_email",
                        },
                        {
                            "name": "Initial",
                            "type_id": record.env.ref("sign.sign_item_type_initial").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.046,
                            "posY": 0.153,
                            "width": 0.080,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Initials",
                            "type_id": record.env.ref("sign.sign_item_type_initial").id,
                            "required": True,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.046,
                            "posY": 0.418 - diff,
                            "width": 0.080,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Business name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.603 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact name",
                            "type_id": record.env.ref("sign.sign_item_type_name").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.633 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": record.env.ref("sign.sign_item_type_phone").name,
                            "type_id": record.env.ref("sign.sign_item_type_phone").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.662 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Email",
                            "type_id": record.env.ref("sign.sign_item_type_email").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.692 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact address",
                            "type_id": record.env.ref(
                                "sign.sign_item_type_multiline_text"
                            ).id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.722 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact city",
                            "type_id": record.env.ref("sign.sign_item_type_text").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.753 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact state",
                            "type_id": record.env.ref("sign.sign_item_type_text").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.781 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact zip",
                            "type_id": record.env.ref("sign.sign_item_type_text").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.811 - diff,
                            "width": 0.429,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                        {
                            "name": "Contact country",
                            "type_id": record.env.ref("sign.sign_item_type_text").id,
                            "required": False,
                            "responsible_id": record.env.ref(
                                "sign.sign_item_role_customer"
                            ).id,
                            "page": 5,
                            "posX": 0.440,
                            "posY": 0.841 - diff,
                            "width": 0.427,
                            "height": 0.020,
                            "template_id": template.id,
                        },
                    ]
                )

            send = False
            without_mail = True
            template_id = template.id
            signers = [
                {
                    "partner_id": record.partner_id.id,
                    "role": record.env.ref("sign.sign_item_role_customer").id,
                }
            ]
            followers = False
            reference = name
            subject = "Please sign the following Cirrus Quotation"
            message = ""

            data = (
                record.env["sign.request"]
                .sudo()
                .initialize_new(
                    template_id,
                    signers,
                    followers,
                    reference,
                    subject,
                    message,
                    send,
                    without_mail,
                )
            )
            sign_request = record.env["sign.request"].browse([data["id"]])
            sign_request.request_item_ids.write({"state": "sent"})
            incomplete_requests = sign_request.request_item_ids.filtered(
                lambda b: b.state != "completed"
            )
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            message = ""
            for inc in incomplete_requests:
                share_url = "%s/sign/document/mail/%s/%s" % (
                    base_url,
                    data["id"],
                    inc.access_token,
                )
                message += "New Sign Request for %s Created: %s\n" % (
                    inc.partner_id.display_name,
                    share_url,
                )
            record.message_post(body=message)
            if record.state == "draft":
                record.state = "sent"
            record.sign_request = False
            return data

    @api.depends(
        "cirruscomplete_selection",
        "controller_id",
        "controller_id.list_price",
        "partner_id",
        "partner_id.country_id",
        "partner_id.country_id.code",
    )
    def _compute_addtl_controller_price(self):
        for order in self:
            price = 0
            if order.controller_id:
                price = order.controller_id.list_price
                additional_fees = ["cir_complete", "cel_upfront"]
                if (
                    order.cirruscomplete_selection
                    and order.cirruscomplete_selection in additional_fees
                ):
                    if order.partner_id.country_id.code == "CA":
                        price = order.controller_id.list_price + 1900
                    else:
                        price = order.controller_id.list_price + 950
            order.addtl_controller_price = price


class SaleOrderRateWizard(models.TransientModel):
    _name = "sale.order.rate.wizard"
    _description = "Sale Order Rate Wizard"

    order_id = fields.Many2one("sale.order", string="Order")
    wizard_line_ids = fields.One2many(
        "sale.order.rate.wizard.line", "wizard_id", string="Wizard Lines"
    )
    auction = fields.Boolean(string="Auction Inc")


class SaleOrderRateWizardLine(models.TransientModel):
    _name = "sale.order.rate.wizard.line"
    _description = "Sale Order Rate Wizard Line"

    wizard_id = fields.Many2one("sale.order.rate.wizard", string="Wizard")
    valid = fields.Boolean(string="Valid")
    carrier_id = fields.Many2one("delivery.carrier", string="Delivery method")
    carrier_code = fields.Char(string="Carrier Code")
    service_code = fields.Char(string="Service Code")
    service_name = fields.Char(string="Service Name")
    calc_method = fields.Char(string="Calc Method")
    rate = fields.Float(string="Rate")
    loaded_rate = fields.Float(string="Loaded Rate")
    other_cost = fields.Float(string="Other Cost")
    list_rate = fields.Float(string="Public Rate")

    def set_rate_on_order(self):
        for record in self:
            if not self.carrier_id:
                raise UserError(
                    _(
                        """This service code is not linked to any Odoo
                        delivery method. Please assocaite this service code
                        to one of the delivery methods."""
                    )
                )
            if record.wizard_id.order_id.client_account:
                set_rate = 0
            elif record.list_rate > 0:
                set_rate = record.list_rate
            else:
                set_rate = record.loaded_rate

            record.wizard_id.order_id.write({"carrier_id": self.carrier_id.id})
            record.wizard_id.order_id.write({"delivery_price": set_rate})
            record.wizard_id.order_id.write({"delivery_rating_success": True})

            return record.wizard_id.order_id.set_delivery_line(self.carrier_id, set_rate)

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _check_amount_and_confirm_order(self):
        self.ensure_one()
        for order in self.sale_order_ids.filtered(
            lambda so: so.state in ("draft", "sent")
        ):
            if order.currency_id.compare_amounts(self.amount, order.amount_total) == 0:
                order.payment_received = True
            else:
                _logger.warning(
                    "<%s> transaction AMOUNT MISMATCH for order %s (ID %s): expected %r, got %r",
                    self.acquirer_id.provider,
                    order.name,
                    order.id,
                    order.amount_total,
                    self.amount,
                )
                order.message_post(
                    subject=_("Amount Mismatch (%s)") % self.acquirer_id.provider,
                    body=_(
                        "The order was not confirmed despite response from the acquirer (%s): order total is %r but acquirer replied with %r."
                    )
                    % (self.acquirer_id.provider, order.amount_total, self.amount,),
                )

