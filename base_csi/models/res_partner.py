# -*- coding: utf-8 -*-

import json
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    salesforce_id = fields.Char(string="Salesforce ID")
    salesforce_parent_id = fields.Char(string="Salesforce Parent ID")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    salesforce_type = fields.Selection(
        [("account", "Account"), ("contact", "Contact")], string="Salesforce Type"
    )
    fax = fields.Char(string="Fax")
    display_count = fields.Integer(
        compute="_compute_display_count", string="Display Count"
    )
    residential = fields.Boolean(string="Residential")
    shipping_account_ids = fields.One2many(
        "res.partner.shipping.account", "partner_id", string="Shipping Accounts"
    )
    shipstation_warehouse_id = fields.Many2one(
        "shipstation.warehouse", string="Shipstation Warehouse"
    )
    attention = fields.Char(string="Attention")
    salesforce_quote_count = fields.Integer(
        string="Quote Count", compute="_get_record_counts"
    )
    salesforce_order_count = fields.Integer(
        string="Order Count", compute="_get_record_counts"
    )
    enterprise_account = fields.Boolean(string="Enterprise")
    sign_shop = fields.Boolean(string="Sign Shop")
    most_recent_order_date = fields.Datetime(
        compute="comoute_most_recent_order_date",
        string="Most Recent Order Date",
        store=True,
    )
    new_sign_shop = fields.Boolean(
        compute="_compute_new_sign_shop", string="New Sign Shop",
    )
    not_new_sign_shop = fields.Boolean(string="Not New Sign Shop", tracking=1)
    hoopla_user = fields.Boolean(string="Hoopla User")

    @api.model
    def _run_new_sign_shop_cron(self):
        _logger.info("Running New Sign Shop Cron")

        # Constants
        entities = self.env["res.partner"]
        today = datetime.now()
        oya = today - timedelta(days=365)
        tya = today - timedelta(days=730)

        # Setting all commercial entities back to False
        reset_entitites = entities.search([("not_new_sign_shop", "=", True)])
        reset_entitites.write({"not_new_sign_shop": False})

        # Searching for records that establish the entity as not new
        sale_orders = self.env["sale.order"].search(
            [
                ("date_order", ">=", tya.strftime("%Y-%m-%d %H:%M:%S")),
                ("date_order", "<", oya.strftime("%Y-%m-%d %H:%M:%S")),
                ("opportunity_id", "!=", False),
                ("state", "in", ["sale", "done"]),
            ]
        )
        salesforce_orders = self.env["salesforce.order"].search(
            [
                ("linked_opp_close_date", ">=", tya.strftime("%Y-%m-%d %H:%M:%S")),
                ("linked_opp_close_date", "<", oya.strftime("%Y-%m-%d %H:%M:%S")),
            ]
        )

        # Consolidating all entities that are not considered new
        entities |= sale_orders.mapped("partner_id.commercial_partner_id")
        entities |= salesforce_orders.mapped("account_name.commercial_partner_id")
        entities |= salesforce_orders.mapped("end_user_account.commercial_partner_id")
        entities |= salesforce_orders.mapped("ship_to_contact.commercial_partner_id")

        # Writing entities as not new
        entities.write({"not_new_sign_shop": True})

    def _compute_new_sign_shop(self):
        for record in self:
            new_sign_shop = True
            if record.not_new_sign_shop:
                new_sign_shop = False
            record.new_sign_shop = new_sign_shop

    @api.depends("sale_order_ids.date_order", "sale_order_ids.state")
    def comoute_most_recent_order_date(self):
        for rec in self:
            rec.most_recent_order_date = False
            partner_id = rec
            if rec.parent_id:
                parent = rec.parent_id
                while parent:
                    partner_id = parent
                    parent = False if not parent.parent_id else parent.parent_id
            if partner_id:
                for partner in self.search([("id", "child_of", partner_id.ids)]):
                    sale_order_ids = self.search(
                        [("id", "child_of", partner.ids)]
                    ).mapped("sale_order_ids")
                    filtered_order = sale_order_ids.filtered(
                        lambda x: x.state in ["sale", "done"]
                    ).sorted(key="date_order", reverse=True)
                    if filtered_order:
                        partner.most_recent_order_date = filtered_order[0].date_order

    @api.onchange("sign_shop")
    def _onchange_sign_shop(self):
        if not self.sign_shop:
            self.new_sign_shop = False

    def _get_record_counts(self):
        for record in self:
            record.salesforce_quote_count = record.env["salesforce.quote"].search_count(
                [
                    "|",
                    "|",
                    ("account__c", "=", record.id),
                    ("account_id", "=", record.id),
                    ("contactid", "=", record.id),
                ]
            )
            record.salesforce_order_count = record.env["salesforce.order"].search_count(
                [
                    "|",
                    "|",
                    ("account_name", "=", record.id),
                    ("end_user_account", "=", record.id),
                    ("ship_to_contact", "=", record.id),
                ]
            )

    def open_salesforce_quote(self):
        self.ensure_one()
        action = self.env.ref("base_csi.action_window_salesforce_quote").read()[0]
        quotes = self.env["salesforce.quote"].search(
            [
                "|",
                "|",
                ("account__c", "=", self.id),
                ("account_id", "=", self.id),
                ("contactid", "=", self.id),
            ]
        )
        action["domain"] = [("id", "in", quotes.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if len(quotes) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = quotes.id
        return action

    def open_salesforce_order(self):
        self.ensure_one()
        action = self.env.ref("base_csi.action_window_salesforce_order").read()[0]
        orders = self.env["salesforce.order"].search(
            [
                "|",
                "|",
                ("account_name", "=", self.id),
                ("end_user_account", "=", self.id),
                ("ship_to_contact", "=", self.id),
            ]
        )
        action["domain"] = [("id", "in", orders.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if len(orders) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = orders.id
        return action

    def create_shipstation_warehouse_id(self, something=False):
        for record in self:
            isitdefault = False
            if record.id == record.env.user.company_id.partner_id.id:
                isitdefault = True
            company = record.env.user.company_id
            url = "%s/warehouses/createwarehouse" % (company.shipstation_root_endpoint)
            address_object = {
                "name": record.name,
                "street1": record.street,
                "street2": record.street2 or None,
                "city": record.city,
                "state": record.state_id.code,
                "postalCode": record.zip,
                "country": record.country_id.code,
                "phone": record.phone or None,
            }
            python_dict = {
                "warehouseName": record.name,
                "originAddress": address_object,
                "returnAddress": address_object,
                "isDefault": isitdefault,
            }
            data_to_post = json.dumps(python_dict)
            conn = company.shipstation_connection(url, "POST", data_to_post)
            response = conn[0]
            content = conn[1]
            if response.status_code != requests.codes.ok:
                raise UserError(_("%s\n%s: %s" % (url, response.status_code, content)))
            json_object_str = content.decode("utf-8")
            json_object = json.loads(json_object_str)
            vals = {
                "partner_id": record.id,
                "name": json_object["warehouseName"],
                "warehouse_id": json_object["warehouseId"],
                "is_default": json_object["isDefault"],
            }
            shipstation_warehouse = record.env["shipstation.warehouse"].create(vals)
            if record.shipstation_warehouse_id:
                record.shipstation_warehouse_id.unlink()
            record.shipstation_warehouse_id = shipstation_warehouse

    def _compute_display_count(self):
        operator = "child_of" if self.is_company else "="
        displays = self.env["display.display"].search(
            [
                "|",
                "|",
                "|",
                "|",
                "|",
                ("distributor", operator, self.id),
                ("sign_shop", operator, self.id),
                ("sign_shop_contact", operator, self.id),
                ("sign_shop_contact", operator, self.id),
                ("account", operator, self.id),
                ("end_user_contact", operator, self.id),
            ]
        )
        self.display_count = len(displays)

    def action_partner_display(self):
        self.ensure_one()
        operator = "child_of" if self.is_company else "="
        domain = [
            "|",
            "|",
            "|",
            "|",
            "|",
            ("distributor", operator, self.id),
            ("sign_shop", operator, self.id),
            ("sign_shop_contact", operator, self.id),
            ("sign_shop_contact", operator, self.id),
            ("account", operator, self.id),
            ("end_user_contact", operator, self.id),
        ]

        return {
            "name": "Display",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "display.display",
            "view_id": False,
            "type": "ir.actions.act_window",
            "domain": domain,
        }
