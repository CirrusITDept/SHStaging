# -*- coding: utf-8 -*-

from odoo import api, fields, models, registry, _
from odoo.exceptions import UserError
import requests
import base64
import json
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from odoo.tools import split_every


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_payment_term_id = fields.Many2one(
        "account.payment.term", string="Default Payment Term"
    )
    repair_location_id = fields.Many2one("stock.location", "Default Repair Location")
    credit_charge_product_id = fields.Many2one(
        "product.product", "Credit Card Fee Product"
    )
    credit_charge_fee = fields.Float(string="Credit Card Fee")
    sale_controller_id = fields.Many2one("product.product", string="Default Controller")
    sale_power_injector_id = fields.Many2one(
        "product.product", string="Default Power Injector"
    )
    sale_wifi_unit_id = fields.Many2one("product.product", string="Default Wifi Unit")
    sale_extension_cable_id = fields.Many2one(
        "product.product", string="Default Extension Cable"
    )
    sale_aluminum_frame_id = fields.Many2one(
        "product.product", string="Default Aluminum Frame"
    )
    sale_led_panel_id = fields.Many2one("product.product", string="Default LED Panel")
    sale_carrier_id = fields.Many2one(
        "delivery.carrier", string="Default Shipping Method"
    )
    sale_module_id = fields.Many2one("product.product", string="Module")
    frame_id = fields.Many2one("product.product", string="Aluminum Frame")
    controller_id = fields.Many2one("product.product", string="Controller")
    booster_id = fields.Many2one("product.product", string="Power Booster")
    wifi_id = fields.Many2one("product.product", string="Wifi Unit")
    shipstation_key = fields.Char(string="SS Key")
    shipstation_secret = fields.Char(string="SS Secret")
    shipstation_root_endpoint = fields.Char(string="SS Root Endpoint")
    shipstation_hook_ids = fields.One2many(
        "shipstation.webhook", "company_id", string="Webhooks"
    )
    target_postback_url = fields.Char(
        string="Postback Target URL",
        placeholder="e.g https://www.odoo.com/shipstation/shipped",
    )
    auto_ss = fields.Boolean(string="Automatic Shipping Label")
    threshold_ids = fields.One2many(
        "purchase.approval.threshold", "company_id", string="Thresholds"
    )
    picking_approvers = fields.Integer(string="# of Picking Approvers Req.")
    hoopla_client_id = fields.Char(string="Hoopla Client ID")
    hoopla_client_secret = fields.Char(string="Hoopla Client Secret")
    hoopla_access_token = fields.Text(string="Hoopla Access Token")
    hoopla_team_id = fields.Selection(
        [("sign_shop", "Sign Shop"), ("sbm", "SMB"), ("enterprise", "Enterprise")],
        string="Hoopla Sales Channel",
        default="sbm",
    )

    def shipstation_connection(self, url, method, data_to_post):
        for record in self:
            if (
                not record.shipstation_root_endpoint
                or not record.shipstation_key
                or not record.shipstation_secret
            ):
                raise UserError(
                    _(
                        "Shipstation API is not configured correctly, make sure all keys and urls are present."
                    )
                )
            api_key = record.shipstation_key
            secret = record.shipstation_secret

            auth_string = (
                base64.encodestring(("%s:%s" % (api_key, secret)).encode())
                .decode()
                .replace("\n", "")
            )

            headers = {"Authorization": "Basic %s" % auth_string}
            if method == "DELETE":
                r = requests.delete(url, headers=headers)
            elif method == "POST":
                headers.update({"Content-Type": "application/json"})
                r = requests.post(url, data=data_to_post, headers=headers)
            else:
                r = requests.get(url, headers=headers)
            return r, r.content

    def shipstation_connection_post(self, url, method, data_to_post):
        for record in self:
            api_key = record.shipstation_key
            secret = record.shipstation_secret

            auth_string = (
                base64.encodestring(("%s:%s" % (api_key, secret)).encode())
                .decode()
                .replace("\n", "")
            )

            headers = {"Authorization": "Basic %s" % auth_string}
            r = requests.get(url, headers=headers)
            content = r.content
            json_object_str = content.decode("utf-8")
            json_object = json.loads(json_object_str)
            for shipment in json_object["shipments"]:
                print(shipment)
                picking = self.env["stock.picking"].browse([int(shipment["orderKey"])])
                if picking:
                    picking.carrier_tracking_ref = shipment["trackingNumber"]
                    picking.message_post(
                        body=_(
                            "<b>Shipstation</b> order to <b>%s</b> w/ tracking number <b>%s</b> cost <b>%s</b>."
                        )
                        % (
                            shipment["shipTo"]["name"],
                            shipment["trackingNumber"],
                            shipment["shipmentCost"],
                        )
                    )
                    if picking.sale_id:
                        picking.sale_id.message_post(
                            body=_(
                                "<b>Shipstation</b> order to <b>%s</b> w/ tracking number <b>%s</b> cost <b>%s</b>."
                            )
                            % (
                                shipment["shipTo"]["name"],
                                shipment["trackingNumber"],
                                shipment["shipmentCost"],
                            )
                        )

    def get_carriers(self):
        for record in self:
            url = "%s/carriers" % (record.shipstation_root_endpoint)
            conn = record.shipstation_connection(url, "GET", False)
            response = conn[0]
            content = conn[1]
            if response.status_code != requests.codes.ok:
                raise UserError(_("%s\n%s: %s" % (url, response.status_code, content)))
            json_object_str = content.decode("utf-8")
            json_object = json.loads(json_object_str)
            carrier_list = []
            for c in json_object:
                carrier_list.append(c["code"])
                if not record.env["delivery.shipstation.carrier"].search(
                    [("carrier_code", "=", c["code"])]
                ):
                    record.env["delivery.shipstation.carrier"].create(
                        {"name": c["name"], "carrier_code": c["code"]}
                    )
            record.subscribe_webhooks()
            record.partner_id.create_shipstation_warehouse_id()
            return carrier_list

    def subscribe_webhooks(self):
        for record in self:
            if not record.get_webhooks():
                url = "%s/webhooks/subscribe" % (record.shipstation_root_endpoint)
                target_url = record.target_postback_url
                python_dict = {
                    "target_url": target_url,
                    "event": "SHIP_NOTIFY",
                    "friendly_name": "Shipment Notification",
                }
                data_to_post = json.dumps(python_dict)
                record.shipstation_connection(url, "POST", data_to_post)
                record.get_webhooks()

    def get_webhooks(self):
        for record in self:
            url = "%s/webhooks" % (record.shipstation_root_endpoint)
            conn = record.shipstation_connection(url, "GET", False)
            response = conn[0]
            content = conn[1]
            if response.status_code != requests.codes.ok:
                raise UserError(_("%s\n%s: %s" % (url, response.status_code, content)))
            json_object_str = content.decode("utf-8")
            json_object = json.loads(json_object_str)
            hooks = json_object["webhooks"]
            if len(hooks) > 0:
                for hook in hooks:
                    if not record.env["shipstation.webhook"].search(
                        [("web_hook_id", "=", int(hook["WebHookID"]))]
                    ):
                        values = {
                            "company_id": record.id,
                            "name": hook["Name"],
                            "url": hook["Url"],
                            "hook_type": hook["HookType"],
                            "web_hook_id": int(hook["WebHookID"]),
                            "active": hook["Active"],
                        }
                        record.env["shipstation.webhook"].create(values)
                return True
            else:
                return False

    def get_hoopla_access_token(self):
        for record in self:
            if (
                not record.hoopla_client_id
                or not record.hoopla_client_secret
                or not record.hoopla_team_id
            ):
                raise UserError(
                    "Missing Hoopla configuration. Please configure these before requesting an authorization token."
                )
            client_for_token = BackendApplicationClient(
                client_id=record.hoopla_client_id
            )
            oauth = OAuth2Session(client=client_for_token)
            token = oauth.fetch_token(
                token_url="https://api.hoopla.net/oauth2/token",
                client_id=record.hoopla_client_id,
                client_secret=record.hoopla_client_secret,
            )
            if token:
                record.hoopla_access_token = token["access_token"]

    @api.model
    def _run_hoopla_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        users_to_update = self.env["res.users"].search(
            [("hoopla_user", "=", True)], limit=None
        )
        company = self.env.user.company_id
        company.get_hoopla_access_token()
        for line_chunk in split_every(10, users_to_update.ids):
            self.env["res.users"].browse(line_chunk)._update_hoopla_metrics()
            if use_new_cursor:
                self._cr.commit()

        if use_new_cursor:
            self._cr.commit()

    @api.model
    def run_hoopla_scheduler(self, use_new_cursor=False, company_id=False):
        try:
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))  # TDE FIXME

            self._run_hoopla_scheduler_tasks(
                use_new_cursor=use_new_cursor, company_id=company_id
            )
        finally:
            if use_new_cursor:
                try:
                    self._cr.close()
                except Exception:
                    pass
        return {}

    def get_service(self):
        for record in self:
            carrier_list = record.get_carriers()
            for c in carrier_list:
                url = "%s/carriers/listservices?carrierCode=%s" % (
                    record.shipstation_root_endpoint,
                    c,
                )
                conn = record.shipstation_connection(url, "GET", False)
                response = conn[0]
                content = conn[1]
                if response.status_code != requests.codes.ok:
                    raise UserError(
                        _("%s\n%s: %s" % (url, response.status_code, content))
                    )
                service = record.env["delivery.carrier"]
                present_service_list = service.search([]).mapped("service_code")
                json_object_str = content.decode("utf-8")
                json_object = json.loads(json_object_str)
                for c in json_object:
                    if c["code"] not in present_service_list:
                        data = {
                            "name": c["name"],
                            "integration_level": False,
                            "carrier_code": record.env["delivery.shipstation.carrier"]
                            .search([("carrier_code", "=", c["carrierCode"])])
                            .id,
                            "service_code": c["code"],
                            "international": c["international"],
                            "domestic": c["domestic"],
                            "created_by_shipstation": True,
                            "product_id": record.env.ref(
                                "delivery.product_product_delivery_product_template"
                            ).product_variant_id.id,
                        }
                        service.create(data)

    def get_packages(self):
        for record in self:
            carrier_list = record.get_carriers()
            for c in carrier_list:
                url = "%s/carriers/listpackages?carrierCode=%s" % (
                    record.shipstation_root_endpoint,
                    c,
                )
                conn = record.shipstation_connection(url, "GET", False)
                response = conn[0]
                content = conn[1]
                if response.status_code != requests.codes.ok:
                    raise UserError(
                        _("%s\n%s: %s" % (url, response.status_code, content))
                    )
                packages = record.env["delivery.shipstation.package"]
                present_package_list = packages.search([]).mapped("code")
                json_object_str = content.decode("utf-8")
                json_object = json.loads(json_object_str)
                for c in json_object:
                    if c["code"] not in present_package_list:
                        data = {
                            "name": c["name"],
                            "carrier_code": record.env["delivery.shipstation.carrier"]
                            .search([("carrier_code", "=", c["carrierCode"])])
                            .id,
                            "code": c["code"],
                            "international": c["international"],
                            "domestic": c["domestic"],
                            "created_by_shipstation": True,
                        }
                        packages.create(data)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Default Payment Term",
        readonly=False,
        related="company_id.sale_payment_term_id",
    )
    repair_location_id = fields.Many2one(
        "stock.location",
        "Default Repair Location",
        readonly=False,
        related="company_id.repair_location_id",
    )
    credit_charge_product_id = fields.Many2one(
        "product.product",
        "Credit Card Fee Product",
        readonly=False,
        related="company_id.credit_charge_product_id",
    )
    credit_charge_fee = fields.Float(
        string="Credit Card Fee", readonly=False, related="company_id.credit_charge_fee"
    )
    sale_controller_id = fields.Many2one(
        "product.product",
        string="Default Controller",
        readonly=False,
        related="company_id.sale_controller_id",
    )
    sale_power_injector_id = fields.Many2one(
        "product.product",
        string="Default Power Injector",
        readonly=False,
        related="company_id.sale_power_injector_id",
    )
    sale_extension_cable_id = fields.Many2one(
        "product.product",
        string="Default Extension Cable",
        readonly=False,
        related="company_id.sale_extension_cable_id",
    )
    sale_wifi_unit_id = fields.Many2one(
        "product.product",
        string="Default Wifi Unit",
        readonly=False,
        related="company_id.sale_wifi_unit_id",
    )
    sale_aluminum_frame_id = fields.Many2one(
        "product.product",
        string="Default Aluminum Frame",
        readonly=False,
        related="company_id.sale_aluminum_frame_id",
    )
    sale_led_panel_id = fields.Many2one(
        "product.product",
        string="Default LED Panel",
        readonly=False,
        related="company_id.sale_led_panel_id",
    )
    sale_carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Default Shipping Method",
        readonly=False,
        related="company_id.sale_carrier_id",
    )
    sale_module_id = fields.Many2one(
        "product.product",
        string="Module",
        readonly=False,
        related="company_id.sale_module_id",
    )
    frame_id = fields.Many2one(
        "product.product",
        string="Aluminum Frame",
        readonly=False,
        related="company_id.frame_id",
    )
    controller_id = fields.Many2one(
        "product.product",
        string="Controller",
        readonly=False,
        related="company_id.controller_id",
    )
    booster_id = fields.Many2one(
        "product.product",
        string="Power Booster",
        readonly=False,
        related="company_id.booster_id",
    )
    wifi_id = fields.Many2one(
        "product.product",
        string="Wifi Unit",
        readonly=False,
        related="company_id.wifi_id",
    )
    shipstation_key = fields.Char(
        string="SS Key", related="company_id.shipstation_key", readonly=False
    )
    shipstation_secret = fields.Char(
        string="SS Secret", related="company_id.shipstation_secret", readonly=False
    )
    shipstation_root_endpoint = fields.Char(
        string="SS Root Endpoint",
        related="company_id.shipstation_root_endpoint",
        readonly=False,
    )
    shipstation_hook_ids = fields.One2many(
        "shipstation.webhook",
        string="Webhooks",
        related="company_id.shipstation_hook_ids",
        readonly=False,
    )
    target_postback_url = fields.Char(
        string="Postback Target URL",
        placeholder="e.g https://www.odoo.com/shipstation/shipped",
        related="company_id.target_postback_url",
        readonly=False,
    )
    auto_ss = fields.Boolean(
        string="Automatic Shipping Label", related="company_id.auto_ss", readonly=False
    )
    picking_approvers = fields.Integer(
        string="# of Picking Approvers Req.",
        readonly=False,
        related="company_id.picking_approvers",
    )
    lost_stage_id = fields.Many2one("crm.stage", "Lost Stage")
    hoopla_client_id = fields.Char(
        string="Hoopla Client ID", readonly=False, related="company_id.hoopla_client_id"
    )
    hoopla_client_secret = fields.Char(
        string="Hoopla Client Secret",
        readonly=False,
        related="company_id.hoopla_client_secret",
    )
    hoopla_access_token = fields.Text(
        string="Hoopla Access Token", related="company_id.hoopla_access_token",
    )
    hoopla_team_id = fields.Selection(
        [("sign_shop", "Sign Shop"), ("sbm", "SMB"), ("enterprise", "Enterprise")],
        string="Hoopla Sales Channel",
        readonly=False,
        related="company_id.hoopla_team_id",
    )

    enable_so_technical_drawings = fields.Boolean(
        string="Enable Sale Order Technical Drawings"
    )

    def get_service(self):
        for record in self:
            record.company_id.get_service()

    def get_hoopla_access_token(self):
        for record in self:
            record.company_id.get_hoopla_access_token()

    def get_packages(self):
        for record in self:
            record.company_id.get_packages()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        lost_stage_id = (
            self.env["ir.config_parameter"].sudo().get_param("base_csi.lost_stage_id")
        )
        enable_so_technical_drawings = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("base_csi.enable_so_technical_drawings")
        )
        res.update(
            lost_stage_id=int(lost_stage_id) if lost_stage_id else False,
            enable_so_technical_drawings=True
            if enable_so_technical_drawings
            else False,
        )
        res.update(lost_stage_id=int(lost_stage_id) if lost_stage_id else False,)
        return res

    @api.model
    def set_values(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "base_csi.lost_stage_id", self.lost_stage_id.id
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "base_csi.enable_so_technical_drawings", self.enable_so_technical_drawings
        )
        super(ResConfigSettings, self).set_values()
