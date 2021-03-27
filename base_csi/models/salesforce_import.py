# -*- coding: utf-8 -*-

import requests
import ast
import csv
import base64
from datetime import datetime
from io import StringIO

from odoo import api, fields, models, registry, _
from odoo.tools import split_every


class SalesforceOrder(models.Model):
    _name = "salesforce.order"
    _description = "Salesforce Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    order_line = fields.One2many(
        "salesforce.order.line", "salesforce_order_id", string="Lines"
    )
    account_name = fields.Many2one("res.partner", string="Account Name")
    additional_emails = fields.Char(string="Additional Emails")
    bill_to_name = fields.Char(string="Bill to Name")
    billing_city = fields.Char(string="Billing City")
    billing_country = fields.Char(string="Billing Country")
    billing_postal_code = fields.Char(string="Billing Postal Code")
    billing_state = fields.Char(string="Billing State")
    billing_street = fields.Char(string="Billing Street")
    ticket_id = fields.Many2one("helpdesk.ticket", string="Case")
    contact_name = fields.Char(string="Contact Name")
    contact_email = fields.Char(string="Contact email")
    controller_id = fields.Char(string="Controller ID")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    description = fields.Text(string="Description")
    display = fields.Many2one("display.display", string="Display")
    do_not_send_email_to_customer = fields.Boolean(
        string="Do Not Send Email To Customer"
    )
    order_start_date = fields.Date(string="Order Start Date")
    end_user_account = fields.Many2one("res.partner", string="End User Account")
    full_sign_replacement = fields.Boolean(string="Full Sign Replacement")
    get_opportunity_name = fields.Char(string="Get Opportunity name")
    salesforce_id = fields.Char(string="Salesforce ID")
    item_quantity = fields.Char(string="Item quantity")
    new_old_order = fields.Char(string="New/Old Order?")
    notes = fields.Text(string="Notes")
    opportunity_id = fields.Many2one("crm.lead", string="Opportunity")
    opportunity_close_date = fields.Date(string="Opportunity Close Date")
    opportunity = fields.Char(string="Opportunity Id")
    name = fields.Char(string="Order Number")
    order_owner = fields.Many2one("res.users", string="Order Owner")
    paid_amount = fields.Char(string="Paid Amount")
    panel_serial_number = fields.Char(string="Panel Serial Number")
    purchase_order_number_rma_number = fields.Char(
        string="Purchase Order Number /RMA Number"
    )
    salesforce_quote_id = fields.Many2one("salesforce.quote", string="Quote")
    recipient_company_name = fields.Char(string="Recipient Company Name")
    recipient_name = fields.Char(string="Recipient Name")
    order_record_type = fields.Char(string="Order Record Type")
    return_aging = fields.Char(string="Return Aging")
    return_completed_date = fields.Date(string="Return Completed Date")
    return_department = fields.Char(string="Return Department")
    return_label_tracking = fields.Char(string="Return Label Tracking")
    return_test = fields.Char(string="Return-Test")
    return_due_date = fields.Date(string="Return Due Date")
    replacement_shipped_date = fields.Date(string="Replacement shipped date")
    service_type = fields.Char(string="Service Type")
    ship_to_contact = fields.Many2one("res.partner", string="Ship To Contact")
    ship_by_date = fields.Date(string="Ship By (Date)")
    ship_date = fields.Date(string="Ship Date")
    ship_to_name = fields.Char(string="Ship to Name")
    shipment_instructions = fields.Char(string="Shipment Instructions")
    shipment_number = fields.Char(string="Shipment Number")
    shipping_city = fields.Char(string="Shipping City")
    shipping_country = fields.Char(string="Shipping Country")
    shipping_postal_code = fields.Char(string="Shipping Postal Code")
    shipping_state = fields.Char(string="Shipping State")
    shipping_street = fields.Char(string="Shipping Street")
    shipping_cost = fields.Char(string="Shipping Cost")
    shipping_service_type = fields.Char(string="Shipping Service Type")
    shipping_speed = fields.Char(string="Shipping Speed")
    status = fields.Char(string="Status")
    order_amount = fields.Char(string="Order Amount")
    tracking_number = fields.Char(string="Tracking number")
    tracking_number2 = fields.Char(string="Tracking number 2")
    order_type = fields.Char(string="Order Type")
    warrantied = fields.Char(string="Warrantied")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", compute="_get_default_currency"
    )
    linked_opp_close_date = fields.Date(string="Linked Opportunity Close Date")

    def _get_default_currency(self):
        for record in self:
            record.currency_id = record.env.ref("base.USD")


class SalesforceOrderLine(models.Model):
    _name = "salesforce.order.line"
    _description = "Salesforce Order Line"

    controller_id__c = fields.Char(string="Controller ID")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    name = fields.Char(string="Line Description")
    salesforce_id = fields.Char(string="Salesforce ID")
    item_cost__c = fields.Char(string="Item Cost")
    list_price = fields.Char(string="List Price")
    salesforce_order_id = fields.Many2one(
        "salesforce.order", string="Salesforce Sale Order"
    )
    order_item_number = fields.Char(string="Order Product Number")
    order_product__c = fields.Char(string="Products Shipped")
    po_reference__c = fields.Char(string="Po Reference")
    qty_owed_partial_orders__c = fields.Char(string="Quantity Shipped")
    quantity = fields.Char(string="Quantity")
    quantity_remaining__c = fields.Char(string="Quantity Remaining")
    shipment_status__c = fields.Char(string="Shipment status")
    total_price = fields.Char(string="Total Price")
    total_cost__c = fields.Char(string="Total Cost")
    tracking_number__c = fields.Char(string="Tracking number")
    unit_price = fields.Char(string="Unit Price")
    zk_weight__c = fields.Char(string="Zk Weight")


class SalesforceQuote(models.Model):
    _name = "salesforce.quote"
    _description = "Salesforce Quote"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    order_line = fields.One2many("salesforce.quote.line", "quoteid", string="Lines")
    account_id = fields.Many2one("res.partner", string="Account Name")
    account_opportunity_new_account__c = fields.Boolean(
        string="Account Opportunity new account"
    )
    account__c = fields.Many2one("res.partner", string="Account")
    balance_due__c = fields.Char(string="Balance Due")
    billingcity = fields.Char(string="Billing City")
    billingcountry = fields.Char(string="Billing Country")
    billingname = fields.Char(string="Bill To Name")
    billingpostalcode = fields.Char(string="Billing Postal Code")
    billingstate = fields.Char(string="Billing State")
    billingstreet = fields.Char(string="Billing Street")
    cellular__c = fields.Boolean(string="Cellular")
    commission_amount__c = fields.Char(string="Commission Amount")
    commission_new_account__c = fields.Char(string="Commission New Account")
    commission_rate__c = fields.Char(string="Commission Rate")
    contactid = fields.Many2one("res.partner", string="Contact Name")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    credit_card_fees__c = fields.Char(string="Credit Card Fees")
    description = fields.Text(string="Description")
    discount = fields.Char(string="Discount")
    email = fields.Char(string="Email")
    estimated_shipping_and_handling__c = fields.Char(
        string="Estimated Shipping and Handling"
    )
    expirationdate = fields.Date(string="Expiration Date")
    fax = fields.Char(string="Fax")
    finalshippingcost__c = fields.Char(string="FinalShippingCost")
    grandtotal = fields.Char(string="Grand Total")
    salesforce_id = fields.Char(string="Salesforce ID")
    invoice_number__c = fields.Char(string="Invoice Number")
    is_sales_shipping__c = fields.Boolean(string="Is Sales Shipping")
    lineitemcount = fields.Char(string="Line Items")
    lineitemshippingcost__c = fields.Char(string="LineItemShippingCost")
    margin_accounting__c = fields.Char(string="Margin (accounting)")
    markup__c = fields.Char(string="Markup(%)")
    max_discount__c = fields.Char(string="Max Discount")
    name = fields.Char(string="Quote Name")
    new_commission_plan__c = fields.Char(string="Commission plan")
    notes__c = fields.Text(string="Notes")
    opportunityid = fields.Many2one("crm.lead", string="Opportunity Name")
    order_generated__c = fields.Boolean(string="Order Generated")
    ownerid = fields.Many2one("res.users", string="Owner Name")
    p_o_number__c = fields.Char(string="P.O Number")
    paid__c = fields.Boolean(string="Paid in Full")
    paid_in_full__c = fields.Boolean(string="Paid in full")
    partial_payment_amount__c = fields.Char(string="Amount Paid")
    payment_method__c = fields.Char(string="Payment Method")
    phone = fields.Char(string="Phone")
    pre_order__c = fields.Boolean(string="Pre-Order")
    product_cost_accounting__c = fields.Char(string="Product Cost(accounting)")
    profit_margin__c = fields.Char(string="Profit Margin")
    purchase_order_number__c = fields.Char(string="Purchase Order")
    quotenumber = fields.Char(string="Quote Number")
    recordtypeid = fields.Char(string="Quote Record Type")
    reference__c = fields.Char(string="Reference:")
    sales_order_number__c = fields.Char(string="Sales Order Number")
    sales_type__c = fields.Char(string="Sales Type")
    shippingcity = fields.Char(string="Shipping City")
    shippingcountry = fields.Char(string="Shipping Country")
    shippinghandling = fields.Char(string="Shipping and Handling")
    shippingname = fields.Char(string="Ship To Name")
    shippingpostalcode = fields.Char(string="Shipping Postal Code")
    shippingstate = fields.Char(string="Shipping State")
    shippingstreet = fields.Char(string="Shipping Street")
    status = fields.Char(string="Status")
    subtotal = fields.Char(string="Subtotal")
    tax = fields.Char(string="Tax")
    terms__c = fields.Char(string="Terms")
    totalprice = fields.Char(string="Total Price")
    total_cost__c = fields.Char(string="Total Product Cost")
    total_price_comm__c = fields.Char(string="Total Price (Commission)")
    total_price_distributor__c = fields.Char(string="Total Price(Distributor)")
    total_shipping_cost__c = fields.Char(string="Shipping Cost")
    total_weight_in_lbs__c = fields.Char(string="Total Weight (Lbs)")
    zone_code__c = fields.Char(string="FedEx Shipping Zone Code")
    zip_value2__c = fields.Char(string="zip value2")
    zip_value3__c = fields.Char(string="zip value3")
    zip_value__c = fields.Char(string="zip value")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", compute="_get_default_currency"
    )

    def _get_default_currency(self):
        for record in self:
            record.currency_id = record.env.ref("base.USD")


class SalesforceQuoteLine(models.Model):
    _name = "salesforce.quote.line"
    _description = "Salesforce Quote Line"

    additional_led_cost__c = fields.Char(string="Additional LED Cost")
    additional_led__c = fields.Char(string="Service Module Quantity")
    average_continuous_power__c = fields.Char(string="Average Continuous Power")
    average_power__c = fields.Char(string="Average Power")
    box_price__c = fields.Char(string="Box Price")
    box_quantity__c = fields.Char(string="Box Quantity")
    box_rate__c = fields.Char(string="Box Rate")
    cabinet_dimensions__c = fields.Char(string="Cabinet Dimensions*:")
    cost_accounting__c = fields.Char(string="Cost (Accounting)")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    name = fields.Char(string="Line Item Description")
    discount = fields.Char(string="Discount")
    display_matrix__c = fields.Char(string="Display Matrix")
    double_single_sided__c = fields.Char(string="Single / Double Sided")
    frames_per_second__c = fields.Char(string="Frames Per Second")
    height__c = fields.Char(string="Height")
    salesforce_id = fields.Char(string="Salesforce ID")
    led_dimensions__c = fields.Char(string="LED Dimensions")
    l__c = fields.Char(string="LED Color")
    linenumber = fields.Char(string="Line Item Number")
    line_item_cost__c = fields.Char(string="Line Item Cost")
    listprice = fields.Char(string="List Price")
    max_power_110v_in_amps__c = fields.Char(string="Max Power @ 110V (in amps)")
    max_power_220v_in_amps__c = fields.Char(string="Max Power @ 220V (in amps)")
    new_shipping_cost__c = fields.Char(string="New Shipping Cost")
    new_product_shipping_cost__c = fields.Char(string="New product Shipping Cost")
    panel_quantity__c = fields.Char(string="Panel Quantity")
    pick_the_right_field_for_panels__c = fields.Char(
        string="Single / Double Sided for quote"
    )
    pixel_pitch__c = fields.Char(string="Pixel Pitch (in mm)")
    product_description__c = fields.Char(string="Product Description")
    product__c = fields.Text(string="Product")
    quantity = fields.Char(string="Quantity")
    quantity_backordered__c = fields.Char(string="Quantity Backordered")
    quantity_shipped__c = fields.Char(string="Quantity Shipped")
    quoteid = fields.Many2one("salesforce.quote", string="Quote Name")
    shipping_cost1__c = fields.Char(string="New Product Shipping Rate1")
    shipping_cost2__c = fields.Char(string="New Product Shipping Rate2")
    shipping_cost3__c = fields.Char(string="New Product Shipping Rate3")
    shipping_cost4__c = fields.Char(string="New Product Shipping Rate4")
    shipping_cost5__c = fields.Char(string="New Product Shipping Rate5")
    shipping_cost6__c = fields.Char(string="New Product Shipping Rate6")
    shipping_cost__c = fields.Char(string="New Product Shipping Rate")
    shipping_rate__c = fields.Char(string="Shipping Rate")
    shipping_product_code__c = fields.Char(string="Shipping product code")
    subtotal = fields.Char(string="Subtotal")
    totalprice = fields.Char(string="Total Price")
    total_price_distributor__c = fields.Char(string="Total Price(Distributor)")
    total_square_feet_per_face__c = fields.Char(string="Total Sq. Ft. (per face)")
    total_weight__c = fields.Char(string="Total Weight")
    unitprice = fields.Char(string="Sales Price")
    viewing_area__c = fields.Char(string="Viewing Area")
    weight_mirror__c = fields.Char(string="Weight Mirror")
    width__c = fields.Char(string="Width")
    wireless_ethernet_bridge_communication__c = fields.Text(
        string="Wireless Ethernet Bridge Communication"
    )


class SalesforceImportFile(models.Model):
    _name = "salesforce.import.file"
    _description = "Salesforce Import File"
    _order = "sequence"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Selection(
        [
            ("user", "User.csv"),
            ("account", "Account.csv"),
            ("contact", "Contact.csv"),
            ("opportunity", "Opportunity.csv"),
            ("lead", "Lead.csv"),
            ("case", "Case.csv"),
            ("case_comment", "CaseComment.csv"),
            ("quote", "Quote.csv"),
            ("quote_line", "QuoteLineItem.csv"),
            ("order", "Order.csv"),
            ("order_line", "OrderItem.csv"),
            ("display_daas", "Display_as_a_Service__c.csv"),
            ("display_setup", "Display2_Information__c.csv"),
            ("display_display", "Display__c.csv"),
            ("car", "CAR__c.csv"),
            ("agreement", "echosign_dev1_SIGN_Agreement__c.csv"),
            ("feed_item", "FeedItem.csv"),
            ("feed_comment", "FeedComment.csv"),
            ("email_message", "EmailMessage.csv"),
        ],
        required=True,
    )
    sequence = fields.Integer(string="Priority", default=10)
    file_id = fields.Binary(string="File", required=True)
    line_ids = fields.One2many("salesforce.import.line", "file_id", string="File Rows")
    upload = fields.Boolean(string="Upload Successful")
    upload_date = fields.Datetime(string="Upload Date")
    line_count = fields.Integer(
        compute="_compute_lines", string="Line Count", copy=False, default=0, store=True
    )
    record_skip = fields.Char(
        string="Records to Skip",
        placeholder="0121N000001Dalw,0121N000001DamL,012o0000000nb2r",
    )

    @api.depends("line_ids")
    def _compute_lines(self):
        for record in self:
            record.line_count = len(record.line_ids)

    def action_view_lines(self):
        action = {
            "name": _("Lines"),
            "type": "ir.actions.act_window",
            "res_model": "salesforce.import.line",
            "target": "current",
        }
        line_ids = self.line_ids.ids
        if len(line_ids) == 1:
            line = line_ids[0]
            action["res_id"] = line
            action["view_mode"] = "form"
            form_view = [
                (self.env.ref("base_csi.view_salesforce_import_line_form").id, "form")
            ]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
        else:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", line_ids)]
        return action

    def _ingest_file(self):
        for record in self:
            myfile = base64.decodestring(record.file_id).decode(
                "latin-1", errors="ignore"
            )
            myfile = myfile.replace("\x00", "")
            f = StringIO(myfile)
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                try:
                    line = str(dict(row))
                    line_dict = {"file_id": record.id, "name": line}
                    record.env["salesforce.import.line"].create(line_dict)
                except Exception as e:
                    message = "Error in importing line:\n%s\n%s" % (e, row)
                    record.message_post(body=message)
            record.upload = True
            record.upload_date = datetime.now()

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        files_to_ingest = self.env["salesforce.import.file"].search(
            [("upload", "=", False)], limit=None
        )
        for file_chunk in split_every(1, files_to_ingest.ids):
            self.env["salesforce.import.file"].browse(file_chunk)._ingest_file()
            if use_new_cursor:
                self._cr.commit()

        if use_new_cursor:
            self._cr.commit()

    @api.model
    def run_scheduler(self, use_new_cursor=False, company_id=False):
        try:
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))  # TDE FIXME

            self._run_scheduler_tasks(
                use_new_cursor=use_new_cursor, company_id=company_id
            )
        finally:
            if use_new_cursor:
                try:
                    self._cr.close()
                except Exception:
                    pass
        return {}


class SalesforceImportLine(models.Model):
    _name = "salesforce.import.line"
    _description = "Salesforce Import File Lines"
    _order = "file_id, last_attempt_date, sequence"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    sequence = fields.Integer(string="Priority", default=10)
    name = fields.Text(string="Line Contents")
    file_id = fields.Many2one("salesforce.import.file", string="File")
    upload = fields.Boolean(string="Upload Successful")
    skip = fields.Boolean(string="Skipped")
    upload_date = fields.Datetime(string="Upload Date")
    update_date = fields.Datetime(string="Last Update Date")
    last_attempt_date = fields.Datetime(string="Last Upload Attempt")
    account_chatter_success = fields.Boolean(string="Account Chatter Uploaded")
    account_chatter_skip = fields.Boolean(string="Account Chatter Skipped")

    def rewrite_records(self):
        false_value = "000000000000000AAA"
        for record in self.filtered(lambda b: not b.skip):
            line = ast.literal_eval(record.name)
            record_type_skip = []
            if record.file_id.record_skip:
                record_type_skip = record.file_id.record_skip.split(",")
            file_type = record.file_id.name
            if "RecordTypeId" in line and line["RecordTypeId"] in record_type_skip:
                record.skip = True
                continue
            # Opportunity.csv
            if file_type == "opportunity":
                search_record = record.env["crm.lead"].search(
                    [("salesforce_id", "=", line["Id"])], limit=1
                )
                if not search_record:
                    continue
                dict_to_write = {}
                if line["Display_ID__c"] and line["Display_ID__c"] != false_value:
                    data_record = record.env["display.display"].search(
                        [("salesforce_id", "=", line["Display_ID__c"])], limit=1
                    )
                    if data_record:
                        dict_to_write.update({"display_id": data_record.id})
                search_record.write(dict_to_write)
            # Case.csv
            if file_type == "case":
                search_record = record.env["helpdesk.ticket"].search(
                    [("salesforce_id", "=", line["Id"])], limit=1
                )
                if not search_record:
                    continue
                dict_to_write = {}
                if line["Display_REAL__c"] and line["Display_REAL__c"] != false_value:
                    data_record = record.env["display.display"].search(
                        [("salesforce_id", "=", line["Display_REAL__c"])], limit=1
                    )
                    if data_record:
                        dict_to_write.update({"display_id": data_record.id})
                search_record.write(dict_to_write)
            # Order.csv
            if file_type == "order":
                search_record = record.env["salesforce.order"].search(
                    [("salesforce_id", "=", line["ID"])], limit=1
                )
                if not search_record:
                    continue
                dict_to_write = {}
                if line["DISPLAY__C"] and line["DISPLAY__C"] != false_value:
                    data_record = record.env["display.display"].search(
                        [("salesforce_id", "=", line["DISPLAY__C"])], limit=1
                    )
                    if data_record:
                        dict_to_write.update({"display": data_record.id})
                search_record.write(dict_to_write)
            # Display__c.csv
            if file_type == "display_display":
                search_record = record.env["display.display"].search(
                    [("salesforce_id", "=", line["Id"])], limit=1
                )
                if not search_record:
                    continue
                dict_to_write = {}
                if line["Opportunity__c"] and line["Opportunity__c"] != false_value:
                    data_record = record.env["crm.lead"].search(
                        [("salesforce_id", "=", line["Opportunity__c"])], limit=1
                    )
                    if data_record:
                        dict_to_write.update({"opportunity": data_record.id})
                search_record.write(dict_to_write)
            # FeedItem.csv
            elif file_type == "feed_item":
                if (
                    line["BODY"]
                    and line["PARENTID"]
                    and line["PARENTID"] != false_value
                ):
                    data_record = record.env["res.partner"].search(
                        [("salesforce_id", "=", line["PARENTID"])], limit=1
                    )
                    if not data_record:
                        record.account_chatter_skip = True
                        continue
                else:
                    record.account_chatter_skip = True
                    continue

                row_dict = {
                    "salesforce_id": line["ID"],
                    "res_id": data_record.id,
                    "model": "res.partner",
                    "body": line["BODY"],
                    "date": datetime.strptime(
                        line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                    ),
                    "message_type": "notification",
                    "subtype_id": 2,
                }

                if line["CREATEDBYID"]:
                    data_record = record.env["res.users"].search(
                        [
                            ("salesforce_id", "=", line["CREATEDBYID"]),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                        limit=1,
                    )
                    if data_record:
                        row_dict.update({"author_id": data_record.partner_id.id})
                    else:
                        row_dict.update({"author_id": 2})
                record.env["mail.message"].create(row_dict)
                record.account_chatter_success = True
            # FeedComment.csv
            elif file_type == "feed_comment":
                data_record = False
                if (
                    line["COMMENTBODY"]
                    and line["PARENTID"]
                    and line["PARENTID"] != false_value
                ):
                    if line["PARENTID"][:3] == "001":
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["PARENTID"])], limit=1
                        )

                if not data_record:
                    record.account_chatter_skip = True
                    continue

                row_dict = {
                    "salesforce_id": line["ID"],
                    "res_id": data_record.id,
                    "model": "res.partner",
                    "body": line["COMMENTBODY"],
                    "date": datetime.strptime(
                        line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                    ),
                    "message_type": "notification",
                    "subtype_id": 2,
                }

                if line["CREATEDBYID"]:
                    data_record = record.env["res.users"].search(
                        [
                            ("salesforce_id", "=", line["CREATEDBYID"]),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                        limit=1,
                    )
                    if data_record:
                        row_dict.update({"author_id": data_record.partner_id.id})
                    else:
                        row_dict.update({"author_id": 2})
                record.env["mail.message"].create(row_dict)
                record.account_chatter_success = True
            record.update_date = datetime.now()
            record.message_post(body="Record has been updated")

    def _ingest_line(self):
        false_value = "000000000000000AAA"
        priority_dict = {
            "Ignore": "0",
            "Low": "0",
            "Medium": "1",
            "High": "2",
            "Emergency": "3",
        }
        for record in self:
            try:
                line = ast.literal_eval(record.name)
                record_type_skip = []
                if record.file_id.record_skip:
                    record_type_skip = record.file_id.record_skip.split(",")
                file_type = record.file_id.name
                if "RecordTypeId" in line and line["RecordTypeId"] in record_type_skip:
                    record.skip = True
                    continue

                # User.csv
                if file_type == "user":
                    user = record.env["res.users"].search(
                        [
                            ("login", "=", line["Username"]),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                        limit=1,
                    )
                    if not user:
                        name = ""
                        if line["FirstName"]:
                            name += "%s " % line["FirstName"]
                        if line["LastName"]:
                            name += line["LastName"]
                        user = record.env["res.users"].create(
                            {
                                "name": name,
                                "login": line["Username"],
                                "salesforce_id": line["Id"],
                            }
                        )
                        user.active = True if line["IsActive"] == "1" else False
                    else:
                        user.salesforce_id = line["Id"]
                        user.active = True if line["IsActive"] == "1" else False
                    record.upload = True
                    record.upload_date = datetime.now()
                    record.update_date = datetime.now()

                # Account.csv
                elif file_type == "account":
                    comment = ""
                    row_dict = {
                        "salesforce_id": line["Id"],
                        "name": line["Name"],
                        "salesforce_parent_id": line["ParentId"],
                        "phone": line["Phone"],
                        "fax": line["Fax"],
                        "website": line["Website"],
                        "salesforce_create_date": line["CreatedDate"],
                        "salesforce_type": "account",
                        "street": line["BillingStreet"],
                        "city": line["BillingCity"],
                        "zip": line["BillingPostalCode"],
                        "is_company": True,
                    }
                    if line["BillingCountry"]:
                        data_record = record.env["res.country"].search(
                            [("code", "=", line["BillingCountry"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"country_id": data_record.id})
                        else:
                            data_record = record.env["res.country"].search(
                                [("name", "=", line["BillingCountry"])], limit=1
                            )
                            if data_record:
                                row_dict.update({"country_id": data_record.id})
                            else:
                                comment = "%sBilling Country: %s\n" % (
                                    comment,
                                    line["BillingCountry"],
                                )
                    if line["BillingState"]:
                        data_record = record.env["res.country.state"].search(
                            [
                                ("code", "=", line["BillingState"]),
                                ("country_id.name", "in", ["United States", "Canada"]),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"state_id": data_record.id})
                        else:
                            data_record = record.env["res.country.state"].search(
                                [
                                    ("name", "=", line["BillingState"]),
                                    (
                                        "country_id.name",
                                        "in",
                                        ["United States", "Canada"],
                                    ),
                                ],
                                limit=1,
                            )
                            if data_record:
                                row_dict.update({"state_id": data_record.id})
                            else:
                                comment = "%sBilling State: %s\n" % (
                                    comment,
                                    line["BillingState"],
                                )
                    if line["OwnerId"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OwnerId"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"user_id": data_record.id})

                    if line["Type"]:
                        data_record = record.env["res.partner.category"].search(
                            [("name", "=", line["Type"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"category_id": [(4, data_record.id)]})
                        else:
                            data_record = record.env["res.partner.category"].create(
                                {"name": line["Type"]}
                            )
                            row_dict.update({"category_id": [(4, data_record.id)]})

                    # Building Notes
                    if line["Description"]:
                        comment = "%s%s\n" % (comment, line["Description"])
                    if line["Notes__c"]:
                        comment = "%s%s\n" % (comment, line["Notes__c"])
                    if line["Marketing_Material_Date_Sent__c"]:
                        comment = "%s%s\n" % (
                            comment,
                            line["Marketing_Material_Date_Sent__c"],
                        )

                    row_dict.update({"comment": comment})
                    record_id = record.env["res.partner"].create(row_dict)

                    # Determine if we need a seperate shipping address
                    if any(
                        [
                            line["BillingStreet"] != line["ShippingStreet"],
                            line["BillingCity"] != line["ShippingCity"],
                            line["BillingState"] != line["ShippingState"],
                            line["BillingPostalCode"] != line["ShippingPostalCode"],
                            line["BillingCountry"] != line["ShippingCountry"],
                        ]
                    ):
                        comment = ""
                        row_dict = {
                            "name": "Shipping",
                            "parent_id": record_id.id,
                            "type": "delivery",
                            "street": line["ShippingStreet"],
                            "city": line["ShippingCity"],
                            "zip": line["ShippingPostalCode"],
                        }
                        if line["ShippingCountry"]:
                            data_record = record.env["res.country"].search(
                                [("code", "=", line["ShippingCountry"])], limit=1
                            )
                            if data_record:
                                row_dict.update({"country_id": data_record.id})
                            else:
                                data_record = record.env["res.country"].search(
                                    [("name", "=", line["ShippingCountry"])], limit=1
                                )
                                if data_record:
                                    row_dict.update({"country_id": data_record.id})
                                else:
                                    comment = "%sShipping Country: %s\n" % (
                                        comment,
                                        line["ShippingCountry"],
                                    )
                        if line["ShippingState"]:
                            data_record = record.env["res.country.state"].search(
                                [
                                    ("code", "=", line["ShippingState"]),
                                    (
                                        "country_id.name",
                                        "in",
                                        ["United States", "Canada"],
                                    ),
                                ],
                                limit=1,
                            )
                            if data_record:
                                row_dict.update({"state_id": data_record.id})
                            else:
                                data_record = record.env["res.country.state"].search(
                                    [
                                        ("name", "=", line["ShippingState"]),
                                        (
                                            "country_id.name",
                                            "in",
                                            ["United States", "Canada"],
                                        ),
                                    ],
                                    limit=1,
                                )
                                if data_record:
                                    row_dict.update({"state_id": data_record.id})
                                else:
                                    comment = "%sShipping State: %s\n" % (
                                        comment,
                                        line["ShippingState"],
                                    )
                        row_dict.update({"comment": comment})
                        record.env["res.partner"].create(row_dict)

                # Contact.csv
                elif file_type == "contact":
                    comment = ""
                    name = line["FirstName"]
                    if line["LastName"]:
                        name = "%s %s" % (name, line["LastName"])
                    row_dict = {
                        "salesforce_id": line["Id"],
                        "name": name,
                        "first_name": line["FirstName"],
                        "last_name": line["LastName"],
                        "street": line["MailingStreet"],
                        "city": line["MailingCity"],
                        "zip": line["MailingPostalCode"],
                        "phone": line["Phone"],
                        "fax": line["Fax"],
                        "mobile": line["MobilePhone"],
                        "email": line["Email"],
                        "function": line["Title"],
                        "comment": line["Description"],
                        "salesforce_create_date": line["CreatedDate"],
                        "salesforce_parent_id": line["AccountId"],
                        "salesforce_type": "contact",
                    }
                    if line["AccountId"] and line["AccountId"] != false_value:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["AccountId"])], limit=1
                        )
                        if data_record:
                            row_dict.update(
                                {"parent_id": data_record.id, "type": "other"}
                            )
                        else:
                            record.skip = True
                            continue
                    else:
                        row_dict.update({"is_company": True})
                    if line["OwnerId"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OwnerId"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"user_id": data_record.id})
                    if line["MailingCountry"]:
                        data_record = record.env["res.country"].search(
                            [("code", "=", line["MailingCountry"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"country_id": data_record.id})
                        else:
                            data_record = record.env["res.country"].search(
                                [("name", "=", line["MailingCountry"])], limit=1
                            )
                            if data_record:
                                row_dict.update({"country_id": data_record.id})
                            else:
                                comment = "%sCountry: %s\n" % (
                                    comment,
                                    line["MailingCountry"],
                                )
                    if line["MailingState"]:
                        data_record = record.env["res.country.state"].search(
                            [
                                ("code", "=", line["MailingState"]),
                                ("country_id.name", "in", ["United States", "Canada"]),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"state_id": data_record.id})
                        else:
                            data_record = record.env["res.country.state"].search(
                                [
                                    ("name", "=", line["MailingState"]),
                                    (
                                        "country_id.name",
                                        "in",
                                        ["United States", "Canada"],
                                    ),
                                ],
                                limit=1,
                            )
                            if data_record:
                                row_dict.update({"state_id": data_record.id})
                            else:
                                comment = "%sState: %s\n" % (
                                    comment,
                                    line["MailingState"],
                                )
                    row_dict.update({"comment": comment})
                    record.env["res.partner"].create(row_dict)

                # Opportunity.csv
                elif file_type == "opportunity":
                    rt_dict = {
                        "0121N000000U1ic": "ScreenHub",
                        "0121N0000019FdC": "Display as a Service",
                        "0121N000001Dain": "LED Displays - Distributor Sales",
                        "012o0000000uCcP": "LED Displays Direct Sales",
                        "012o00000015XtDi": "LED Displays",
                    }
                    sale_team = record.env["crm.team"].search(
                        [("salesforce_id", "=", line["RecordTypeId"])], limit=1
                    )
                    if not sale_team:
                        st_name = rt_dict.get(line["RecordTypeId"], False)
                        if not st_name:
                            st_name = line["RecordTypeId"]
                        sale_team = record.env["crm.team"].create(
                            {
                                "name": st_name,
                                "salesforce_id": line["RecordTypeId"],
                                "use_quotations": True,
                                "use_opportunities": True,
                                "use_leads": True,
                            }
                        )
                    comment = ""
                    partner_id = False
                    if line["ContactId"] and line["ContactId"] != false_value:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["ContactId"])], limit=1
                        )
                        if data_record:
                            partner_id = data_record.id
                    if (
                        not partner_id
                        and line["Contact_Name__c"]
                        and line["Contact_Name__c"] != false_value
                    ):
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["Contact_Name__c"])], limit=1
                        )
                        if data_record:
                            partner_id = data_record.id
                    if (
                        not partner_id
                        and line["AccountId"]
                        and line["AccountId"] != false_value
                    ):
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["AccountId"])], limit=1
                        )
                        if data_record:
                            partner_id = data_record.id
                    amount = 0
                    if line["Amount"]:
                        amount = float(line["Amount"])
                    probability = 0
                    if line["Probability"]:
                        probability = float(line["Probability"])

                    row_dict = {
                        "salesforce_id": line["Id"],
                        "partner_id": partner_id,
                        "name": line["Name"],
                        "planned_revenue": amount,
                        "probability": probability,
                        "date_deadline": line["CloseDate"],
                        "salesforce_create_date": line["CreatedDate"],
                        "type": "opportunity",
                        "team_id": sale_team.id,
                    }

                    if int(line["IsClosed"]) == 1 and int(line["IsWon"]) == 1:
                        row_dict.update({"won_status": "won"})
                    elif int(line["IsClosed"]) == 1 and int(line["IsWon"]) != 1:
                        row_dict.update({"won_status": "lost"})
                    else:
                        row_dict.update({"won_status": "pending"})

                    if line["State__c"]:
                        data_record = record.env["res.country.state"].search(
                            [
                                ("code", "=", line["State__c"]),
                                ("country_id.name", "in", ["United States", "Canada"]),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"dest_state_id": data_record.id})
                        else:
                            data_record = record.env["res.country.state"].search(
                                [
                                    ("name", "=", line["State__c"]),
                                    (
                                        "country_id.name",
                                        "in",
                                        ["United States", "Canada"],
                                    ),
                                ],
                                limit=1,
                            )
                            if data_record:
                                row_dict.update({"dest_state_id": data_record.id})
                            else:
                                comment = "%s Dest. State: %s\n" % (
                                    comment,
                                    line["State__c"],
                                )
                    if line["OwnerId"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OwnerId"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"user_id": data_record.id})

                    if line["StageName"]:
                        data_record = record.env["crm.stage"].search(
                            [("name", "=", line["StageName"])], limit=1
                        )
                        if not data_record:
                            seq = 10
                            if line["StageSortOrder"]:
                                seq = int(line["StageSortOrder"])
                            data_record = record.env["crm.stage"].create(
                                {"name": line["StageName"], "sequence": seq}
                            )
                        row_dict.update({"stage_id": data_record.id})

                    if line["Lost_Opportunity_Reason__c"]:
                        data_record = record.env["crm.lost.reason"].search(
                            [("name", "=", line["Lost_Opportunity_Reason__c"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["crm.lost.reason"].create(
                                {"name": line["Lost_Opportunity_Reason__c"]}
                            )
                        row_dict.update({"lost_reason": data_record.id})

                    payment_method = False
                    if line["Payment_Met__c"]:
                        data_record = record.env["account.payment.term"].search(
                            [("name", "=", line["Payment_Met__c"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["account.payment.term"].create(
                                {"name": line["Payment_Met__c"]}
                            )
                        row_dict.update({"payment_term_id": data_record.id})
                        payment_method = True
                    if line["Payment_Terms__c"] and not payment_method:
                        data_record = record.env["account.payment.term"].search(
                            [("name", "=", line["Payment_Terms__c"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["account.payment.term"].create(
                                {"name": line["Payment_Terms__c"]}
                            )
                        row_dict.update({"payment_term_id": data_record.id})
                    # Building Notes
                    if line["Description"]:
                        comment = "%s%s\n" % (comment, line["Description"])
                    if line["Summary__c"]:
                        comment = "%s%s\n" % (comment, line["Summary__c"])
                    if line["End_User_Information__c"]:
                        comment = "%s%s\n" % (comment, line["End_User_Information__c"])
                    if line["Display_ID__c"]:
                        comment = "%s%s\n" % (comment, line["Display_ID__c"])
                    row_dict.update({"description": comment})
                    record.env["crm.lead"].create(row_dict)
                # Lead.csv
                elif file_type == "lead":
                    rt_dict = {
                        "0121N000000U1ic": "ScreenHub",
                        "0121N0000019FdC": "Display as a Service",
                        "0121N000001Dain": "LED Displays - Distributor Sales",
                        "012o0000000uCcP": "LED Displays Direct Sales",
                        "012o00000015XtDi": "LED Displays",
                    }
                    sale_team = record.env["crm.team"].search(
                        [("salesforce_id", "=", line["RecordTypeId"])], limit=1
                    )
                    if not sale_team:
                        st_name = rt_dict.get(line["RecordTypeId"], False)
                        if not st_name:
                            st_name = line["RecordTypeId"]
                        sale_team = record.env["crm.team"].create(
                            {
                                "name": st_name,
                                "salesforce_id": line["RecordTypeId"],
                                "use_quotations": True,
                                "use_opportunities": True,
                                "use_leads": True,
                            }
                        )
                    comment = ""
                    name = line["FirstName"]
                    if line["LastName"]:
                        name = "%s %s" % (name, line["LastName"])
                    lead_name = name
                    if line["Company"]:
                        lead_name = "%s (%s)" % (lead_name, line["Company"])
                    row_dict = {
                        "name": lead_name,
                        "contact_name": name,
                        "salesforce_id": line["Id"],
                        "first_name": line["FirstName"],
                        "last_name": line["LastName"],
                        "function": line["Title"],
                        "partner_name": line["Company"],
                        "street": line["Street"],
                        "city": line["City"],
                        "zip": line["PostalCode"],
                        "phone": line["Phone"],
                        "mobile": line["MobilePhone"],
                        "email_from": line["Email"],
                        "website": line["Website"],
                        "salesforce_create_date": line["CreatedDate"],
                        "type": "lead",
                        "user_id": False,
                        "team_id": sale_team.id,
                    }
                    if line["OwnerId"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OwnerId"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"user_id": data_record.id})

                    if line["Country"]:
                        data_record = record.env["res.country"].search(
                            [("code", "=", line["Country"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"country_id": data_record.id})
                        else:
                            data_record = record.env["res.country"].search(
                                [("name", "=", line["Country"])], limit=1
                            )
                            if data_record:
                                row_dict.update({"country_id": data_record.id})
                            else:
                                comment = "%sCountry: %s\n" % (comment, line["Country"])
                    if line["State"]:
                        data_record = record.env["res.country.state"].search(
                            [
                                ("code", "=", line["State"]),
                                ("country_id.name", "in", ["United States", "Canada"]),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"state_id": data_record.id})
                        else:
                            data_record = record.env["res.country.state"].search(
                                [
                                    ("name", "=", line["State"]),
                                    (
                                        "country_id.name",
                                        "in",
                                        ["United States", "Canada"],
                                    ),
                                ],
                                limit=1,
                            )
                            if data_record:
                                row_dict.update({"state_id": data_record.id})
                            else:
                                comment = "%sState: %s\n" % (comment, line["State"])
                    if line["LeadSource"]:
                        data_record = record.env["utm.source"].search(
                            [("name", "=", line["LeadSource"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["utm.source"].create(
                                {"name": line["LeadSource"]}
                            )
                        row_dict.update({"source_id": data_record.id})
                    if line["Status"]:
                        data_record = record.env["crm.lead.tag"].search(
                            [("name", "=", line["Status"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["crm.lead.tag"].create(
                                {"name": line["Status"]}
                            )
                        row_dict.update({"tag_ids": [(4, data_record.id)]})

                    if line["Description"]:
                        comment = "%s%s\n" % (comment, line["Description"])
                    row_dict.update({"description": comment})
                    record.env["crm.lead"].create(row_dict)
                # Case.csv
                elif file_type == "case":
                    rt_dict = {
                        "012o0000000yGQ6": "Inquiry",
                        "012o0000000yGQB": "Software",
                        "012o0000000yGQG": "Hardware",
                        "012o0000000yGSW": "Internet",
                        "012o0000000yGmq": "Install",
                        "012o0000000yHBv": "Unknown",
                    }
                    help_team = record.env["helpdesk.team"].search(
                        [("salesforce_id", "=", line["RecordTypeId"])], limit=1
                    )
                    if not help_team:
                        st_name = rt_dict.get(line["RecordTypeId"], False)
                        if not st_name:
                            st_name = line["RecordTypeId"]
                        help_team = record.env["helpdesk.team"].create(
                            {"name": st_name, "salesforce_id": line["RecordTypeId"]}
                        )
                    partner_id = partner_sign_id = partner_dist_id = False
                    if line["ContactId"] and line["ContactId"] != false_value:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["ContactId"])], limit=1
                        )
                        if data_record:
                            partner_id = data_record.id
                    if (
                        not partner_id
                        and line["AccountId"]
                        and line["AccountId"] != false_value
                    ):
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["AccountId"])], limit=1
                        )
                        if data_record:
                            partner_id = data_record.id

                    if line["Sign_Shop__c"] and line["Sign_Shop__c"] != false_value:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["Sign_Shop__c"])], limit=1
                        )
                        if data_record:
                            partner_sign_id = data_record.id
                        else:
                            data_record = record.env["res.partner"].search(
                                [("salesforce_id", "=", line["Sign_Shop__c"])], limit=1
                            )
                            if data_record:
                                partner_sign_id = data_record.id
                    if line["Distributor__c"] and line["Distributor__c"] != false_value:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["Distributor__c"])], limit=1
                        )
                        if data_record:
                            partner_sign_id = data_record.id
                        else:
                            data_record = record.env["res.partner"].search(
                                [("salesforce_id", "=", line["Distributor__c"])],
                                limit=1,
                            )
                            if data_record:
                                partner_sign_id = data_record.id

                    row_dict = {
                        "salesforce_id": line["Id"],
                        "salesforce_case_number": line["CaseNumber"],
                        "salesforce_create_date": line["CreatedDate"],
                        "partner_id": partner_id,
                        "partner_name": line["SuppliedName"],
                        "partner_email": line["SuppliedEmail"],
                        "partner_phone": line["SuppliedPhone"],
                        "name": line["Subject"],
                        "priority": priority_dict.get(line["Priority"], "0"),
                        "internal_description": line["Description"],
                        "partner_sign_id": partner_sign_id,
                        "partner_dist_id": partner_dist_id,
                        "next_action": line["Next_Action__c"],
                        "team_id": help_team.id,
                    }

                    if line["ClosedDate"]:
                        row_dict.update({"close_date": line["ClosedDate"]})
                    if line["OwnerId"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OwnerId"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"user_id": data_record.id})

                    helpdesk_tag_list = []

                    if line["Tech_Updates__c"]:
                        data_record = record.env["helpdesk.tag"].search(
                            [("name", "=", line["Tech_Updates__c"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["helpdesk.tag"].create(
                                {"name": line["Tech_Updates__c"]}
                            )
                        helpdesk_tag_list.append(data_record.id)
                    if line["Connection_Type__c"]:
                        data_record = record.env["helpdesk.tag"].search(
                            [("name", "=", line["Connection_Type__c"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["helpdesk.tag"].create(
                                {"name": line["Connection_Type__c"]}
                            )
                        helpdesk_tag_list.append(data_record.id)
                    if line["Reason"]:
                        data_record = record.env["helpdesk.tag"].search(
                            [("name", "=", line["Reason"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["helpdesk.tag"].create(
                                {"name": line["Reason"]}
                            )
                        helpdesk_tag_list.append(data_record.id)

                    if len(helpdesk_tag_list) > 0:
                        row_dict.update({"tag_ids": [(6, 0, helpdesk_tag_list)]})
                    if line["Type"]:
                        data_record = record.env["helpdesk.ticket.type"].search(
                            [("name", "=", line["Type"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["helpdesk.ticket.type"].create(
                                {"name": line["Type"]}
                            )
                        row_dict.update({"ticket_type_id": data_record.id})
                    if line["Status"]:
                        data_record = record.env["helpdesk.stage"].search(
                            [("name", "=", line["Status"])], limit=1
                        )
                        if not data_record:
                            data_record = record.env["helpdesk.stage"].create(
                                {"name": line["Status"]}
                            )
                        row_dict.update({"stage_id": data_record.id})
                    record.env["helpdesk.ticket"].create(row_dict)
                # CaseComment.csv
                elif file_type == "case_comment":
                    if line["ParentId"] and line["ParentId"] != false_value:
                        data_record = record.env["helpdesk.ticket"].search(
                            [("salesforce_id", "=", line["ParentId"])], limit=1
                        )
                        if not data_record:
                            continue
                    else:
                        continue

                    row_dict = {
                        "salesforce_id": line["Id"],
                        "res_id": data_record.id,
                        "model": "helpdesk.ticket",
                        "body": line["CommentBody"],
                        "date": line["CreatedDate"],
                        "message_type": "notification",
                        "subtype_id": 2,
                    }

                    if line["CreatedById"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["CreatedById"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"author_id": data_record.partner_id.id})
                        else:
                            row_dict.update({"author_id": 2})
                    record.env["mail.message"].create(row_dict)

                # Quote.csv
                elif file_type == "quote":
                    row_dict = {
                        "account_opportunity_new_account__c": bool(
                            line["ACCOUNT_OPPORTUNITY_NEW_ACCOUNT__C"]
                        ),
                        "cellular__c": bool(line["CELLULAR__C"]),
                        "is_sales_shipping__c": bool(line["IS_SALES_SHIPPING__C"]),
                        "order_generated__c": bool(line["ORDER_GENERATED__C"]),
                        "paid__c": bool(line["PAID__C"]),
                        "paid_in_full__c": bool(line["PAID_IN_FULL__C"]),
                        "pre_order__c": bool(line["PRE_ORDER__C"]),
                        "billingcity": line["BILLINGCITY"],
                        "billingcountry": line["BILLINGCOUNTRY"],
                        "billingname": line["BILLINGNAME"],
                        "billingpostalcode": line["BILLINGPOSTALCODE"],
                        "billingstate": line["BILLINGSTATE"],
                        "billingstreet": line["BILLINGSTREET"],
                        "commission_new_account__c": line["COMMISSION_NEW_ACCOUNT__C"],
                        "email": line["EMAIL"],
                        "fax": line["FAX"],
                        "salesforce_id": line["ID"],
                        "invoice_number__c": line["INVOICE_NUMBER__C"],
                        "name": line["NAME"],
                        "new_commission_plan__c": line["NEW_COMMISSION_PLAN__C"],
                        "p_o_number__c": line["P_O_NUMBER__C"],
                        "phone": line["PHONE"],
                        "purchase_order_number__c": line["PURCHASE_ORDER_NUMBER__C"],
                        "quotenumber": line["QUOTENUMBER"],
                        "reference__c": line["REFERENCE__C"],
                        "sales_order_number__c": line["SALES_ORDER_NUMBER__C"],
                        "shippingcity": line["SHIPPINGCITY"],
                        "shippingcountry": line["SHIPPINGCOUNTRY"],
                        "shippingname": line["SHIPPINGNAME"],
                        "shippingpostalcode": line["SHIPPINGPOSTALCODE"],
                        "shippingstate": line["SHIPPINGSTATE"],
                        "shippingstreet": line["SHIPPINGSTREET"],
                        "payment_method__c": line["PAYMENT_METHOD__C"],
                        "recordtypeid": line["RECORDTYPEID"],
                        "sales_type__c": line["SALES_TYPE__C"],
                        "status": line["STATUS"],
                        "terms__c": line["TERMS__C"],
                        "expirationdate": line["EXPIRATIONDATE"]
                        if line["EXPIRATIONDATE"]
                        else False,
                        "salesforce_create_date": datetime.strptime(
                            line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "commission_rate__c": line["COMMISSION_RATE__C"],
                        "discount": line["DISCOUNT"],
                        "markup__c": line["MARKUP__C"],
                        "max_discount__c": line["MAX_DISCOUNT__C"],
                        "total_weight_in_lbs__c": line["TOTAL_WEIGHT_IN_LBS__C"],
                        "balance_due__c": line["BALANCE_DUE__C"],
                        "commission_amount__c": line["COMMISSION_AMOUNT__C"],
                        "credit_card_fees__c": line["CREDIT_CARD_FEES__C"],
                        "estimated_shipping_and_handling__c": line[
                            "ESTIMATED_SHIPPING_AND_HANDLING__C"
                        ],
                        "finalshippingcost__c": line["FINALSHIPPINGCOST__C"],
                        "grandtotal": line["GRANDTOTAL"],
                        "margin_accounting__c": line["MARGIN_ACCOUNTING__C"],
                        "partial_payment_amount__c": line["PARTIAL_PAYMENT_AMOUNT__C"],
                        "product_cost_accounting__c": line[
                            "PRODUCT_COST_ACCOUNTING__C"
                        ],
                        "profit_margin__c": line["PROFIT_MARGIN__C"],
                        "shippinghandling": line["SHIPPINGHANDLING"],
                        "subtotal": line["SUBTOTAL"],
                        "tax": line["TAX"],
                        "totalprice": line["TOTALPRICE"],
                        "total_cost__c": line["TOTAL_COST__C"],
                        "total_price_comm__c": line["TOTAL_PRICE_COMM__C"],
                        "total_price_distributor__c": line[
                            "TOTAL_PRICE_DISTRIBUTOR__C"
                        ],
                        "total_shipping_cost__c": line["TOTAL_SHIPPING_COST__C"],
                        "lineitemcount": line["LINEITEMCOUNT"],
                        "lineitemshippingcost__c": line["LINEITEMSHIPPINGCOST__C"],
                        "zone_code__c": line["ZONE_CODE__C"],
                        "zip_value2__c": line["ZIP_VALUE2__C"],
                        "zip_value3__c": line["ZIP_VALUE3__C"],
                        "zip_value__c": line["ZIP_VALUE__C"],
                        "description": line["DESCRIPTION"],
                        "notes__c": line["NOTES__C"],
                    }

                    if line["OWNERID"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OWNERID"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"ownerid": data_record.id})
                    if line["ACCOUNT__C"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["ACCOUNT__C"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"account__c": data_record.id})
                    if line["ACCOUNTID"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["ACCOUNTID"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"account_id": data_record.id})
                    if line["CONTACTID"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["CONTACTID"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"contactid": data_record.id})
                    if line["OPPORTUNITYID"]:
                        data_record = record.env["crm.lead"].search(
                            [("salesforce_id", "=", line["OPPORTUNITYID"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"opportunityid": data_record.id})
                    record.env["salesforce.quote"].create(row_dict)

                # QuoteLineItem.csv
                elif file_type == "quote_line":
                    if line["QUOTEID"] and line["QUOTEID"] != false_value:
                        data_record = record.env["salesforce.quote"].search(
                            [("salesforce_id", "=", line["QUOTEID"])], limit=1
                        )
                        if not data_record:
                            continue
                    else:
                        continue

                    row_dict = {
                        "additional_led_cost__c": line["ADDITIONAL_LED_COST__C"],
                        "additional_led__c": line["ADDITIONAL_LED__C"],
                        "average_continuous_power__c": line[
                            "AVERAGE_CONTINUOUS_POWER__C"
                        ],
                        "average_power__c": line["AVERAGE_POWER__C"],
                        "box_price__c": line["BOX_PRICE__C"],
                        "box_quantity__c": line["BOX_QUANTITY__C"],
                        "box_rate__c": line["BOX_RATE__C"],
                        "cabinet_dimensions__c": line["CABINET_DIMENSIONS__C"],
                        "cost_accounting__c": line["COST_ACCOUNTING__C"],
                        "salesforce_create_date": datetime.strptime(
                            line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "name": line["DESCRIPTION"],
                        "discount": line["DISCOUNT"],
                        "display_matrix__c": line["DISPLAY_MATRIX__C"],
                        "double_single_sided__c": line["DOUBLE_SINGLE_SIDED__C"],
                        "frames_per_second__c": line["FRAMES_PER_SECOND__C"],
                        "height__c": line["HEIGHT__C"],
                        "salesforce_id": line["ID"],
                        "led_dimensions__c": line["LED_DIMENSIONS__C"],
                        "l__c": line["L__C"],
                        "linenumber": line["LINENUMBER"],
                        "line_item_cost__c": line["LINE_ITEM_COST__C"],
                        "listprice": line["LISTPRICE"],
                        "max_power_110v_in_amps__c": line["MAX_POWER_110V_IN_AMPS__C"],
                        "max_power_220v_in_amps__c": line["MAX_POWER_220V_IN_AMPS__C"],
                        "new_shipping_cost__c": line["NEW_SHIPPING_COST__C"],
                        "new_product_shipping_cost__c": line[
                            "NEW_PRODUCT_SHIPPING_COST__C"
                        ],
                        "panel_quantity__c": line["PANEL_QUANTITY__C"],
                        "pick_the_right_field_for_panels__c": line[
                            "PICK_THE_RIGHT_FIELD_FOR_PANELS__C"
                        ],
                        "pixel_pitch__c": line["PIXEL_PITCH__C"],
                        "product_description__c": line["PRODUCT_DESCRIPTION__C"],
                        "product__c": line["PRODUCT__C"],
                        "quantity": line["QUANTITY"],
                        "quantity_backordered__c": line["QUANTITY_BACKORDERED__C"],
                        "quantity_shipped__c": line["QUANTITY_SHIPPED__C"],
                        "quoteid": data_record.id,
                        "shipping_cost1__c": line["SHIPPING_COST1__C"],
                        "shipping_cost2__c": line["SHIPPING_COST2__C"],
                        "shipping_cost3__c": line["SHIPPING_COST3__C"],
                        "shipping_cost4__c": line["SHIPPING_COST4__C"],
                        "shipping_cost5__c": line["SHIPPING_COST5__C"],
                        "shipping_cost6__c": line["SHIPPING_COST6__C"],
                        "shipping_cost__c": line["SHIPPING_COST__C"],
                        "shipping_rate__c": line["SHIPPING_RATE__C"],
                        "shipping_product_code__c": line["SHIPPING_PRODUCT_CODE__C"],
                        "subtotal": line["SUBTOTAL"],
                        "totalprice": line["TOTALPRICE"],
                        "total_price_distributor__c": line[
                            "TOTAL_PRICE_DISTRIBUTOR__C"
                        ],
                        "total_square_feet_per_face__c": line[
                            "TOTAL_SQUARE_FEET_PER_FACE__C"
                        ],
                        "total_weight__c": line["TOTAL_WEIGHT__C"],
                        "unitprice": line["UNITPRICE"],
                        "viewing_area__c": line["VIEWING_AREA__C"],
                        "weight_mirror__c": line["WEIGHT_MIRROR__C"],
                        "width__c": line["WIDTH__C"],
                        "wireless_ethernet_bridge_communication__c": line[
                            "WIRELESS_ETHERNET_BRIDGE_COMMUNICATION__C"
                        ],
                    }
                    record.env["salesforce.quote.line"].create(row_dict)
                # Order.csv
                elif file_type == "order":
                    row_dict = {
                        "do_not_send_email_to_customer": bool(
                            line["DO_NOT_SEND_EMAIL_TO_CUSTOMER__C"]
                        ),
                        "full_sign_replacement": bool(
                            line["FULL_SIGN_REPLACEMENT_DEL__C"]
                        ),
                        "additional_emails": line["ADDITIONAL_EMAILS__C"],
                        "bill_to_name": line["BILL_TO_NAME2__C"],
                        "billing_city": line["BILLINGCITY"],
                        "billing_country": line["BILLINGCOUNTRY"],
                        "billing_postal_code": line["BILLINGPOSTALCODE"],
                        "billing_state": line["BILLINGSTATE"],
                        "billing_street": line["BILLINGSTREET"],
                        "contact_name": line["CONTACT_NAME__C"],
                        "contact_email": line["CONTACT_EMAIL__C"],
                        "controller_id": line["CONTROLLER_ID__C"],
                        "get_opportunity_name": line["GET_OPPORTUNITY_NAME__C"],
                        "salesforce_id": line["ID"],
                        "new_old_order": line["NEW_OLD_ORDER__C"],
                        "opportunity": line["OPPORTUNITY_ID__C"],
                        "name": line["ORDERNUMBER"],
                        "panel_serial_number": line["PANEL_SERIAL_NUMBER__C"],
                        "purchase_order_number_rma_number": line[
                            "PURCHASE_ORDER_NUMBER__C"
                        ],
                        "recipient_company_name": line["RECIPIENT_COMPANY_NAME__C"],
                        "recipient_name": line["RECIPIENT_NAME__C"],
                        "order_record_type": line["RECORDTYPEID"],
                        "return_department": line["RETURN_DEPARTMENT_DEL__C"],
                        "return_label_tracking": line["RETURN_LABEL_TRACKING__C"],
                        "return_test": line["RETURN_TEST__C"],
                        "service_type": line["SERVICE_TYPE__C"],
                        "ship_to_name": line["SHIP_TO_NAME__C"],
                        "shipment_instructions": line["SHIPMENT_INSTRUCTIONS__C"],
                        "shipment_number": line["SHIPMENT_NUMBER__C"],
                        "shipping_city": line["SHIPPINGCITY"],
                        "shipping_country": line["SHIPPINGCOUNTRY"],
                        "shipping_postal_code": line["SHIPPINGPOSTALCODE"],
                        "shipping_state": line["SHIPPINGSTATE"],
                        "shipping_street": line["SHIPPINGSTREET"],
                        "shipping_service_type": line["SHIPPING_SERVICE_TYPE__C"],
                        "shipping_speed": line["SHIPPING_SPEED__C"],
                        "status": line["STATUS"],
                        "tracking_number2": line["TRACKING_NUMBER2__C"],
                        "tracking_number": line["TRACKING_NUMBER__C"],
                        "order_type": line["TYPE"],
                        "warrantied": line["WARRANTIED__C"],
                        "order_start_date": line["EFFECTIVEDATE"]
                        if line["EFFECTIVEDATE"]
                        else False,
                        "opportunity_close_date": line["OPPORTUNITY_CLOSE_DATE__C"]
                        if line["OPPORTUNITY_CLOSE_DATE__C"]
                        else False,
                        "return_completed_date": line["RETURN_COMPLETED_DATE__C"]
                        if line["RETURN_COMPLETED_DATE__C"]
                        else False,
                        "return_due_date": line["RETURN__C"]
                        if line["RETURN__C"]
                        else False,
                        "replacement_shipped_date": line["RETURNED_ITEM_SHIPPED__C"]
                        if line["RETURNED_ITEM_SHIPPED__C"]
                        else False,
                        "ship_by_date": line["SHIP_BY_DATE__C"]
                        if line["SHIP_BY_DATE__C"]
                        else False,
                        "ship_date": line["SHIP_DATE__C"]
                        if line["SHIP_DATE__C"]
                        else False,
                        "salesforce_create_date": datetime.strptime(
                            line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "paid_amount": line["PAID_AMOUNT__C"],
                        "shipping_cost": line["SHIPPING_COST__C"],
                        "order_amount": line["TOTALAMOUNT"],
                        "item_quantity": line["ITEM_QUANTITY__C"],
                        "return_aging": line["RETURN_AGING__C"],
                        "description": line["DESCRIPTION"],
                        "notes": line["NOTES__C"],
                    }

                    if line["OWNERID"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OWNERID"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"order_owner": data_record.id})
                    if line["QUOTEID"]:
                        data_record = record.env["salesforce.quote"].search(
                            [("salesforce_id", "=", line["QUOTEID"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"salesforce_quote_id": data_record.id})
                    if line["SHIPTOCONTACTID"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["SHIPTOCONTACTID"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"ship_to_contact": data_record.id})
                    if line["ACCOUNTID"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["ACCOUNTID"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"account_name": data_record.id})
                    if line["END_USER_ACCOUNT__C"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["END_USER_ACCOUNT__C"])],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"end_user_account": data_record.id})
                    if line["OPPORTUNITYID"]:
                        data_record = record.env["crm.lead"].search(
                            [("salesforce_id", "=", line["OPPORTUNITYID"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"opportunity_id": data_record.id})
                    if line["CASE__C"]:
                        data_record = record.env["helpdesk.ticket"].search(
                            [("salesforce_id", "=", line["CASE__C"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"ticket_id": data_record.id})
                    if line["DISPLAY__C"]:
                        data_record = record.env["display.display"].search(
                            [("salesforce_id", "=", line["DISPLAY__C"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"display": data_record.id})
                    record.env["salesforce.order"].create(row_dict)

                # OrderItem.csv
                elif file_type == "order_line":
                    if line["ORDERID"] and line["ORDERID"] != false_value:
                        data_record = record.env["salesforce.order"].search(
                            [("salesforce_id", "=", line["ORDERID"])], limit=1
                        )
                        if not data_record:
                            continue
                    else:
                        continue

                    row_dict = {
                        "controller_id__c": line["CONTROLLER_ID__C"],
                        "salesforce_create_date": datetime.strptime(
                            line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "name": line["DESCRIPTION"],
                        "salesforce_id": line["ID"],
                        "item_cost__c": line["ITEM_COST__C"],
                        "list_price": line["LISTPRICE"],
                        "salesforce_order_id": data_record.id,
                        "order_item_number": line["ORDERITEMNUMBER"],
                        "order_product__c": line["ORDER_PRODUCT__C"],
                        "po_reference__c": line["PO_REFERENCE__C"],
                        "qty_owed_partial_orders__c": line[
                            "QTY_OWED_PARTIAL_ORDERS__C"
                        ],
                        "quantity": line["QUANTITY"],
                        "quantity_remaining__c": line["QUANTITY_REMAINING__C"],
                        "shipment_status__c": line["SHIPMENT_STATUS__C"],
                        "total_price": line["TOTALPRICE"],
                        "total_cost__c": line["TOTAL_COST__C"],
                        "tracking_number__c": line["TRACKING_NUMBER__C"],
                        "unit_price": line["UNITPRICE"],
                        "zk_weight__c": line["ZK_WEIGHT__C"],
                    }
                    record.env["salesforce.order.line"].create(row_dict)

                # Display_as_a_Service__c.csv
                elif file_type == "display_daas":
                    row_dict = {
                        "salesforce_id": line["Id"],
                        "salesforce_create_date": line["CreatedDate"],
                        "name": line["Name"],
                    }
                    record.env["display.daas"].create(row_dict)

                # Display2_Information__c.csv
                elif file_type == "display_setup":
                    row_dict = {
                        "cloud_account_created": line["Cloud_Account_Created__c"],
                        "cloud_account_linked_to_controller": line[
                            "Cloud_Account_linked_to_controller__c"
                        ],
                        "eu_completed": line["EUcompleted__c"],
                        "install_completed": line["Install_Completed__c"],
                        "installerinfo": line["Installerinfo__c"],
                        "internet_connection_info_completed": line[
                            "Internet_Connection_Info_completed__c"
                        ],
                        "it_support_completed": line["IT_support_completed__c"],
                        "loaded_to_the_install_map": line[
                            "Loaded_to_the_install_map__c"
                        ],
                        "completed": line["Completed__c"],
                        "reconfirmed": line["Reconfirmed__c"],
                        "account_email": line["Account_Email__c"],
                        "city": line["City__c"],
                        "contact_email": line["Contact_Email__c"],
                        "contact_phone_number": line["Contact_Phone_Number__c"],
                        "controller_id": line["Controller_ID__c"],
                        "country": line["Country__c"],
                        "display_id": line["Display_ID__c"],
                        "name": line["Name"],
                        "end_user_email": line["End_User_Email__c"],
                        "end_user_name": line["End_User_name__c"],
                        "end_user_phone": line["End_User_Phone__c"],
                        "salesforce_id": line["Id"],
                        "it_contact_email": line["It_contact_email__c"],
                        "it_contact_name": line["It_Contact_Name__c"],
                        "it_contact_phone": line["IT_contact_Phone__c"],
                        "length_of_ethernet_cable": line["Length_of_Ethernet_Cable__c"],
                        "other_email": line["Other_email__c"],
                        "password": line["password__c"],
                        "pixel_matrix": line["Pixel_Matrix__c"],
                        "project_owner_email": line["ProjectOwner__c"],
                        "purchase_order": line["Purchase_Order__c"],
                        "sign_shop_name": line["Sign_Shop_Name__c"],
                        "state": line["State__c"],
                        "tracking_nu": line["Tracking_nu__c"],
                        "username": line["Username__c"],
                        "website": line["Website__c"],
                        "zip_c": line["ZIP__c"],
                        "cloud_completed_date": line["cloud_completed_date__c"]
                        if line["cloud_completed_date__c"]
                        else False,
                        "cloud_training_completed": line["Cloud_Training_Completed__c"]
                        if line["Cloud_Training_Completed__c"]
                        else False,
                        "estimated_install_date": line["Estimated_install_date__c"]
                        if line["Estimated_install_date__c"]
                        else False,
                        "installed_date": line["Installed_date__c"]
                        if line["Installed_date__c"]
                        else False,
                        "installer_information_completed_date": line[
                            "Installer_information_completed_date__c"
                        ]
                        if line["Installer_information_completed_date__c"]
                        else False,
                        "internet_connection_info_completed_date": line[
                            "Internet_Connection_Info_completed_date__c"
                        ]
                        if line["Internet_Connection_Info_completed_date__c"]
                        else False,
                        "it_support_completed_date": line[
                            "IT_support_completed_date__c"
                        ]
                        if line["IT_support_completed_date__c"]
                        else False,
                        "cloud_walk_scheduled_for": line["Cloud_walk_scheduled_for__c"]
                        if line["Cloud_walk_scheduled_for__c"]
                        else False,
                        "salesforce_create_date": line["CreatedDate"],
                        "completed_date": line["Completed_date__c"]
                        if line["Completed_date__c"]
                        else False,
                        "internet_call_time": line["Internet_Call_time__c"]
                        if line["Internet_Call_time__c"]
                        else False,
                        "it_support_call": line["It_Support_Call__c"]
                        if line["It_Support_Call__c"]
                        else False,
                        "display_address": line["Display_Address__c"],
                        "display_notes": line["Display_Notes__c"],
                        "how_will_it_be_mounted": line["How_will_it_be_mounted__c"],
                        "notes": line["Notes__c"],
                        "internet_connection_notes": line[
                            "Internet_connection_notes__c"
                        ],
                        "display_height": line["Display_Height__c"],
                        "display_width": line["Display_Width__c"],
                        "can_they_do_video": line["Can_they_do_video__c"],
                        "cirrus_system_model": line["Cirrus_System_Model__c"],
                        "direct_line_of_site_from_antenna_to_sign": line[
                            "Direct_line_of_site_from_antenna_to_sign__c"
                        ],
                        "X00019226": line["X00019226__c"],
                        "display_info_stage": line["Display_Info_Stage__c"],
                        "end_s_user_info": line["End_s_User_Indo__c"],
                        "free_content_status": line["Free_Content_Status__c"],
                        "got_it_contact_info": line["Got_IT_Contact_info__c"],
                        "has_a_survey_site_been_completed": line[
                            "Has_a_survey_site_been_completed__c"
                        ],
                        "install_checklist_stage": line["Install_checklist_stage__c"],
                        "internet": line["Internet__c"],
                        "internet_connection_stage": line[
                            "Internet_Connection_Stage__c"
                        ],
                        "it_support": line["It_Support__c"],
                        "n2_has_an_outlet_been_installed": line[
                            "N2_Has_an_outlet_been_installed__c"
                        ],
                        "new_retrofit": line["New_Retrofit__c"],
                        "order_type": line["Order_Type__c"],
                        "responsible_for_internet_connectivity": line[
                            "Responsible_for_internet_connectivity__c"
                        ],
                        "responsible_for_led_cloud_account": line[
                            "Responsible_for_LED_Cloud_Account__c"
                        ],
                        "sign_shop_needs_an_led_cloud_training": line[
                            "Sign_shop_needs_an_LED_cloud_training__c"
                        ],
                        "single_double_sided": line["Single_Double_Sided__c"],
                        "stage_on_all": line["Stage_on_all__c"],
                        "test_in_shop": line["Test_in_Shop__c"],
                        "they_have_ethernet_cables": line[
                            "They_have_Ethernet_cables__c"
                        ],
                        "to_run_new_electric": line["To_run_new_electric__c"],
                        "any_ideas_for_content": line["Any_ideas_for_content__c"],
                        "contact_name": line["Contact_Name__c"],
                        "network_restrictions": line["Network_restrictions__c"],
                        "opportunity_description": line["Opportunity_Description__c"],
                        "sales_notes": line["Sales_Notes__c"],
                        "opportunity_end_user_notes": line[
                            "Opportunity_End_user_notes__c"
                        ],
                        "it_contact_if_they_are_responsible": line[
                            "IT_Contact_If_they_are_responsible__c"
                        ],
                    }
                    if line["ProjectOwner__c"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["ProjectOwner__c"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"project_owner": data_record.id})
                    if line["Order__c"]:
                        data_record = record.env["salesforce.order"].search(
                            [("salesforce_id", "=", line["Order__c"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"salesforce_order": data_record.id})
                    if line["Opportunity__c"]:
                        data_record = record.env["crm.lead"].search(
                            [("salesforce_id", "=", line["Opportunity__c"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"opportunity": data_record.id})

                    record.env["display.setup"].create(row_dict)
                # Display__c.csv
                elif file_type == "display_display":
                    daas = record.env["display.daas"].search(
                        [("salesforce_id", "=", line["Display_as_a_Service__c"])],
                        limit=1,
                    )
                    setup = record.env["display.setup"].search(
                        [("salesforce_id", "=", line["Display_Setup__c"])], limit=1
                    )
                    row_dict = {
                        "display_as_a_service": daas.id,
                        "display_setup": setup.id,
                        "cellular_enabled": line["Cellular_Enabled__c"],
                        "cellular_paid": line["Cellular_Paid__c"],
                        "display_name": line["Display_ID__c"],
                        "name": line["Name"],
                        "salesforce_id": line["Id"],
                        "it_contact_email": line["IT_Contact_Email__c"],
                        "it_contact_name": line["IT_Contact_Name__c"],
                        "it_contact_phone": line["IT_Contact_Phone__c"],
                        "number_of_power_injectors": line[
                            "Number_of_Power_Injectors__c"
                        ],
                        "screenhub_2_0_display_id": line["ScreenHub_2_0_Display_ID__c"],
                        "screenhub_display_id": line["Screenhub_Display_ID__c"],
                        "software_version": line["Software_Version__c"],
                        "cellular_enabled_until": line["Cellular_Enabled_Until__c"]
                        if line["Cellular_Enabled_Until__c"]
                        else False,
                        "install_date": line["Install_Date__c"]
                        if line["Install_Date__c"]
                        else False,
                        "projected_install_date": line["Projected_Install_Date__c"]
                        if line["Projected_Install_Date__c"]
                        else False,
                        "purchase_date": line["Purchase_Date__c"]
                        if line["Purchase_Date__c"]
                        else False,
                        "salesforce_create_date": line["CreatedDate"],
                        "details": line["Details__c"],
                        "electrical_details": line["Electrical_details__c"],
                        "hardware": line["Hardware__c"],
                        "network_settings_restrictions": line[
                            "Network_Settings_Restrictions__c"
                        ],
                        "physical_notes": line["Physical_Notes__c"],
                        "breaker_rating": int(float(line["Breaker_Rating__c"]))
                        if line["Breaker_Rating__c"]
                        else 0,
                        "distance_from_building": int(
                            float(line["Distance_from_Building__c"])
                        )
                        if line["Distance_from_Building__c"]
                        else 0,
                        "download_speed": int(float(line["Download_Speed__c"]))
                        if line["Download_Speed__c"]
                        else 0,
                        "height": int(float(line["Height__c"]))
                        if line["Height__c"]
                        else 0,
                        "height_from_ground": int(float(line["Height_from_Ground__c"]))
                        if line["Height_from_Ground__c"]
                        else 0,
                        "upload_speed": int(float(line["Upload_Speed__c"]))
                        if line["Upload_Speed__c"]
                        else 0,
                        "width": int(float(line["Width__c"]))
                        if line["Width__c"]
                        else 0,
                        "application": line["Application__c"],
                        "controller_mounting_location": line[
                            "Controller_Mounting_Location__c"
                        ],
                        "end_user_responsible_for_electrical": line[
                            "End_user_responsible_for_electrical__c"
                        ],
                        "end_user_responsible_for_internet": line[
                            "End_user_responsible_for_internet__c"
                        ],
                        "hardware_type": line["Hardware_Type__c"],
                        "internet_connection_type": line["Internet_Connection_Type__c"],
                        "internet_speed_class": line["Internet_Speed_Class__c"],
                        "labor_warranty": line["Labor_Warranty__c"],
                        "screenhub_version": line["ScreenHub_Version__c"],
                        "model": line["Model__c"],
                        "mounting_type": line["Mounting_Type__c"],
                        "new_electrical_line": line["New_Electrical_Line__c"],
                        "number_of_faces": line["Number_of_faces__c"],
                        "own_dedicated_circuit": line["Own_Dedicated_Circuit__c"],
                        "panel_control_software": line["Panel_Control_Software__c"],
                        "firmware_version": line["Firmware_Version__c"],
                        "pitch": line["Pitch__c"],
                        "sign_shop_responsible_for_electric": line[
                            "Sign_shop_responsible_for_electric__c"
                        ],
                        "sign_shop_responsible_for_internet": line[
                            "Sign_shop_responsible_for_internet__c"
                        ],
                        "status_old": line["Status__c"],
                        "electical_setup_voltage": line["Electical_Setup_Voltage__c"],
                        "additional_digital_details": line[
                            "Additional_Digital_Details__c"
                        ],
                    }
                    if line["OwnerId"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OwnerId"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"owner_id": data_record.id})
                    if line["Distributor__c"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["Distributor__c"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"distributor": data_record.id})
                    if line["Account__c"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["Account__c"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"account": data_record.id})
                    if line["End_User_Contact__c"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["End_User_Contact__c"])],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"end_user_contact": data_record.id})
                    if line["Sign_Shop__c"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["Sign_Shop__c"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"sign_shop": data_record.id})
                    if line["Sign_Shop_Contact__c"]:
                        data_record = record.env["res.partner"].search(
                            [("salesforce_id", "=", line["Sign_Shop_Contact__c"])],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"sign_shop_contact": data_record.id})
                    if line["Opportunity__c"]:
                        data_record = record.env["crm.lead"].search(
                            [("salesforce_id", "=", line["Opportunity__c"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"opportunity": data_record.id})

                    record.env["display.display"].create(row_dict)
                # CAR__c.csv
                elif file_type == "car":
                    row_dict = {
                        "car_completed": line["CAR_COMPLETED__C"],
                        "nonconformity_affirmed": line["INITIAL_REVIEW_AFFIRMED__C"],
                        "nonconformity_not_affirmed": line[
                            "INITIAL_REVIEW_NOT_AFFIRMED__C"
                        ],
                        "review_pending": line["REVIEW_PENDING__C"],
                        "controller_id_number": line["CONTROLLER_ID__C"],
                        "salesforce_id": line["ID"],
                        "module_serial_number": line["MODULE_SERIAL_NUMBER__C"],
                        "name": line["NAME"],
                        "salesforce_create_date": datetime.strptime(
                            line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "description": line["NONCONFORMITY_SUMMARY__C"],
                        "action_corrective": line["CORRECTIVE_ACTION_S__C"],
                        "disposition_instructions_if_applicable": line[
                            "DISPOSITION_INSTRUCTIONS_IF_APPLICABLE__C"
                        ],
                        "root_cause_analysis": line["ROOT_CAUSE_ANALYSIS__C"],
                        "component_faults": line["COMPONENT_FAULTS__C"],
                        "controller_faults": line["CONTROLLER_FAULTS__C"],
                        "known_problems_for_panels": line[
                            "KNOWN_PROBLEM_FOR_PANELS__C"
                        ],
                        "known_problems_for_controllers": line[
                            "KNOWN_PROBLEMS_FOR_CONTROLLERS__C"
                        ],
                        "panel_faults": line["PANEL_FAULTS__C"],
                    }
                    if line["DISPOSITION_OPTIONS__C"]:
                        opt_list = []
                        options = line["DISPOSITION_OPTIONS__C"].split(";")
                        for opt in options:
                            data_record = record.env[
                                "quality.disposition.option"
                            ].search([("name", "=", opt)], limit=1)
                            if not data_record:
                                data_record = record.env[
                                    "quality.disposition.option"
                                ].create({"name": opt})
                            opt_list.append(data_record.id)
                        row_dict.update({"disposition_options": [(6, 0, opt_list)]})
                    if line["OWNERID"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["OWNERID"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"user_id": data_record.id})
                    if line["ORDER__C"]:
                        data_record = record.env["salesforce.order"].search(
                            [("salesforce_id", "=", line["ORDER__C"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"salesforce_order": data_record.id})
                    if line["CASE__C"]:
                        data_record = record.env["helpdesk.ticket"].search(
                            [("salesforce_id", "=", line["CASE__C"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"ticket_id": data_record.id})
                    if line["STATUS__C"]:
                        data_record = record.env["quality.alert.stage"].search(
                            [("name", "=", line["STATUS__C"])], limit=1
                        )
                        if data_record:
                            row_dict.update({"stage_id": data_record.id})
                        else:
                            data_record = record.env["quality.alert.stage"].create(
                                {"name": line["STATUS__C"]}
                            )
                            row_dict.update({"stage_id": data_record.id})

                    if line["RECORDTYPEID"]:
                        record_dict = {
                            "0121N000001fxv0QAA": "Panel(s)",
                            "0121N000001fxv5QAA": "Component(s)",
                            "0121N000001fxvAQAQ": "Controller(s)",
                        }
                        rtype = record_dict.get(line["RECORDTYPEID"], False)
                        row_dict.update({"car_type": rtype})

                    record.env["quality.alert"].create(row_dict)
                # CAR__c.csv
                elif file_type == "agreement":
                    if line["DISPLAY__C"] and line["DISPLAY__C"] != false_value:
                        data_record = record.env["display.display"].search(
                            [("salesforce_id", "=", line["DISPLAY__C"])], limit=1
                        )
                        if data_record and line["ECHOSIGN_DEV1__SIGNEDPDF__C"]:
                            response = requests.get(line["ECHOSIGN_DEV1__SIGNEDPDF__C"])
                            output_byte = response.content
                            report_name = "%s.pdf" % line["NAME"]
                            record.env["ir.attachment"].create(
                                {
                                    "name": report_name,
                                    "store_fname": report_name,
                                    "datas": base64.encodestring(output_byte),
                                    "res_model": "display.display",
                                    "res_id": data_record.id,
                                    "type": "binary",
                                    "url": "url",
                                    "mimetype": "application/pdf",
                                }
                            )
                # FeedItem.csv
                elif file_type == "feed_item":
                    model = False
                    if (
                        line["BODY"]
                        and line["PARENTID"]
                        and line["PARENTID"] != false_value
                    ):
                        data_record = record.env["helpdesk.ticket"].search(
                            [("salesforce_id", "=", line["PARENTID"])], limit=1
                        )
                        model = "helpdesk.ticket"
                        if not data_record:
                            data_record = record.env["salesforce.order"].search(
                                [("salesforce_id", "=", line["PARENTID"])], limit=1
                            )
                            model = "salesforce.order"
                            if not data_record:
                                data_record = record.env["display.display"].search(
                                    [("salesforce_id", "=", line["PARENTID"])], limit=1
                                )
                                model = "display.display"
                                if not data_record:
                                    record.skip = True
                                    continue
                    else:
                        record.skip = True
                        continue

                    row_dict = {
                        "salesforce_id": line["ID"],
                        "res_id": data_record.id,
                        "model": model,
                        "body": line["BODY"],
                        "date": datetime.strptime(
                            line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ),
                        "message_type": "notification",
                        "subtype_id": 2,
                    }

                    if line["CREATEDBYID"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["CREATEDBYID"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"author_id": data_record.partner_id.id})
                        else:
                            row_dict.update({"author_id": 2})
                    record.env["mail.message"].create(row_dict)
                # FeedComment.csv
                elif file_type == "feed_comment":
                    model = data_record = False
                    if (
                        line["COMMENTBODY"]
                        and line["PARENTID"]
                        and line["PARENTID"] != false_value
                    ):
                        if line["PARENTID"][:3] == "500":
                            data_record = record.env["helpdesk.ticket"].search(
                                [("salesforce_id", "=", line["PARENTID"])], limit=1
                            )
                            model = "helpdesk.ticket"
                        elif line["PARENTID"][:3] == "801":
                            data_record = record.env["salesforce.order"].search(
                                [("salesforce_id", "=", line["PARENTID"])], limit=1
                            )
                            model = "salesforce.order"
                        elif line["PARENTID"][:3] == "a0D":
                            data_record = record.env["display.display"].search(
                                [("salesforce_id", "=", line["PARENTID"])], limit=1
                            )
                            model = "display.display"

                    if not data_record or not model:
                        record.skip = True
                        continue

                    row_dict = {
                        "salesforce_id": line["ID"],
                        "res_id": data_record.id,
                        "model": model,
                        "body": line["COMMENTBODY"],
                        "date": datetime.strptime(
                            line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ),
                        "message_type": "notification",
                        "subtype_id": 2,
                    }

                    if line["CREATEDBYID"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["CREATEDBYID"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"author_id": data_record.partner_id.id})
                        else:
                            row_dict.update({"author_id": 2})
                    record.env["mail.message"].create(row_dict)
                # EmailMessage.csv
                elif file_type == "email_message":
                    data_record = False
                    model = "helpdesk.ticket"
                    if (
                        line["HTMLBODY"]
                        and line["PARENTID"]
                        and line["PARENTID"] != false_value
                    ):
                        data_record = record.env["helpdesk.ticket"].search(
                            [("salesforce_id", "=", line["PARENTID"])], limit=1
                        )

                    if not data_record or not model:
                        record.skip = True
                        continue

                    row_dict = {
                        "salesforce_id": line["ID"],
                        "res_id": data_record.id,
                        "model": model,
                        "body": line["HTMLBODY"],
                        "date": datetime.strptime(
                            line["CREATEDDATE"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ),
                        "message_type": "notification",
                        "subtype_id": 2,
                    }

                    if line["CREATEDBYID"]:
                        data_record = record.env["res.users"].search(
                            [
                                ("salesforce_id", "=", line["CREATEDBYID"]),
                                "|",
                                ("active", "=", True),
                                ("active", "=", False),
                            ],
                            limit=1,
                        )
                        if data_record:
                            row_dict.update({"author_id": data_record.partner_id.id})
                        else:
                            row_dict.update({"author_id": 2})
                    record.env["mail.message"].create(row_dict)
                record.upload = True
                record.last_attempt_date = datetime.now()
                record.upload_date = datetime.now()

            except Exception as e:
                message = "Error in importing line:\n%s" % (e)
                record.last_attempt_date = datetime.now()
                record.message_post(body=message)

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        lines_to_ingest = self.env["salesforce.import.line"].search(
            [("upload", "=", False), ("skip", "=", False)], limit=None
        )
        for line_chunk in split_every(100, lines_to_ingest.ids):
            self.env["salesforce.import.line"].browse(line_chunk)._ingest_line()
            if use_new_cursor:
                self._cr.commit()

        if use_new_cursor:
            self._cr.commit()

    @api.model
    def run_scheduler(self, use_new_cursor=False, company_id=False):
        try:
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))  # TDE FIXME

            self._run_scheduler_tasks(
                use_new_cursor=use_new_cursor, company_id=company_id
            )
        finally:
            if use_new_cursor:
                try:
                    self._cr.close()
                except Exception:
                    pass
        return {}
