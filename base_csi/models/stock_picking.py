from odoo import fields, api, models, _
from odoo.exceptions import UserError
import datetime
import json
import requests
import base64
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
import logging

_logger = logging.getLogger(__name__)


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    count_helpdesk_value = fields.Integer(compute="_compute_helpdesk_value")
    count_sale_order_value = fields.Integer(compute="_compute_sale_order_value")
    picking_operation = fields.Boolean(string="Use as Picking Operation")
    delivery_operation = fields.Boolean(string="Use as Delivery Operation")

    def _compute_helpdesk_value(self):
        for rec in self:
            rec.count_helpdesk_value = False
            helpdesk_picking_id = rec.env["stock.picking"].search(
                [
                    "|",
                    ("picking_operation", "=", True),
                    ("delivery_operation", "=", True),
                    ("state", "=", "assigned"),
                    ("ticket_id", "!=", False),
                    ("picking_type_id", "=", rec.id),
                ]
            )
            rec.count_helpdesk_value = len(helpdesk_picking_id)

    def _compute_sale_order_value(self):
        for rec in self:
            rec.count_sale_order_value = False
            sale_picking_id = rec.env["stock.picking"].search(
                [
                    "|",
                    ("picking_operation", "=", True),
                    ("delivery_operation", "=", True),
                    ("state", "=", "assigned"),
                    ("ticket_id", "=", False),
                    ("picking_type_id", "=", rec.id),
                ]
            )
            rec.count_sale_order_value = len(sale_picking_id)

    def action_helpdesk_picking_tree_ready(self):
        return self._get_action("base_csi.action_helpdesk_picking_tree_ready")

    def action_sale_order_picking_tree_ready(self):
        return self._get_action("base_csi.action_sale_order_picking_tree_ready")


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.constrains("product_uom_qty", "quantity_done", "product_id")
    def add_dimensions_to_picking(self):
        for record in self.filtered(lambda b: b.picking_id):
            record.picking_id.calc_dimensions()


class StockPickingApproval(models.Model):
    _name = "stock.picking.approval"

    picking_id = fields.Many2one("stock.picking", string="Picking")
    name = fields.Many2one("res.users", string="Approver")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_operation = fields.Boolean(
        string="Use as Picking Operation", related="picking_type_id.picking_operation"
    )
    delivery_operation = fields.Boolean(
        string="Use as Delivery Operation", related="picking_type_id.delivery_operation"
    )
    is_cancel = fields.Boolean()
    approval_ids = fields.One2many(
        "stock.picking.approval", "picking_id", string="Approvals"
    )
    approved = fields.Boolean(string="Approved", compute="_approved_picking")
    ss_id = fields.Integer(string="Shipstation ID", copy=False)
    return_ss_id = fields.Integer(string="Return Shipstation ID", copy=False)
    ss_ship_id = fields.Integer(string="Shipment ID", copy=False)
    return_ss_ship_id = fields.Integer(string="Return Shipment ID", copy=False)
    ss_status = fields.Selection(
        [
            ("awaiting_payment", "Awaiting Payment"),
            ("awaiting_shipment", "Awaiting Shipment"),
            ("shipped", "Shipped"),
            ("on_hold", "On Hold"),
            ("cancelled", "Cancelled"),
        ],
        string="Shipstation Status",
        copy=False,
    )
    return_ss_status = fields.Selection(
        [
            ("awaiting_payment", "Awaiting Payment"),
            ("awaiting_shipment", "Awaiting Shipment"),
            ("shipped", "Shipped"),
            ("on_hold", "On Hold"),
            ("cancelled", "Cancelled"),
        ],
        string="Return Shipstation Status",
        copy=False,
    )
    ss_address_status = fields.Selection(
        [
            ("Address not yet validated", "Address not Validated"),
            ("Address validated successfully", "Address Validated"),
            ("Address validation warning", "Address Validation Warning"),
            ("Address validation failed", "Address Validation Failed"),
        ],
        string="Shipstation Address",
        copy=False,
    )
    return_ss_address_status = fields.Selection(
        [
            ("Address not yet validated", "Address not Validated"),
            ("Address validated successfully", "Address Validated"),
            ("Address validation warning", "Address Validation Warning"),
            ("Address validation failed", "Address Validation Failed"),
        ],
        string="Return Shipstation Address",
        copy=False,
    )
    confirmation = fields.Selection(
        [
            ("none", "None"),
            ("delivery", "Delivery"),
            ("signature", "Signature"),
            ("adult_signature", "Adult Signature"),
            ("direct_signature", "Direct Signature"),
        ],
        string="Confirmation method",
        default="none",
        copy=False,
    )
    client_account = fields.Many2one(
        "res.partner.shipping.account", string="Client Shipping Acct"
    )
    delivery_package = fields.Many2one(
        "delivery.shipstation.package", string="Delivery Package"
    )
    delivery_carrier_code = fields.Many2one(
        "delivery.shipstation.carrier",
        string="Carrier Code",
        related="carrier_id.carrier_code",
    )
    delivery_length = fields.Float(string="Length")
    delivery_width = fields.Float(string="Width")
    delivery_height = fields.Float(string="Height")
    document_url = fields.Char("Document URL")
    return_document_url = fields.Char("Return Document URL")
    ss_order_weight = fields.Float("Override Weight")
    return_location = fields.Boolean(
        string="Return Location", store=True, related="location_dest_id.return_location"
    )
    salesforce_order = fields.Many2one("salesforce.order", string="Salesforce Order")
    ticket_id = fields.Many2one("helpdesk.ticket", string="Helpdesk Ticket")
    return_picking_id = fields.Many2one("stock.picking", string="Return Order")
    return_carrier_tracking_ref = fields.Char(string="Return Tracking #")

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        res["is_cancel"] = False
        return res

    def unreserve_lot_sn(self):
        for picking in self:
            picking.move_lines.filtered(
                lambda x: x.product_id.tracking in ["lot", "serial"]
            )._do_unreserve()

    def button_validate(self):
        self.ensure_one()
        attachment = self.env["ir.attachment"].search(
            [("res_id", "=", self.id), ("res_model", "=", "stock.picking")]
        )
        if not attachment and self.picking_type_id.code == "outgoing":
            raise UserError(
                _("""Please upload the required files before validating.""")
            )
        if (
            not attachment
            and self.picking_type_id.code == "incoming"
            and self.ticket_id
        ):
            raise UserError(
                _(
                    """This receipt cannot be validated because there is no attachment. Please upload the required files before validating."""
                )
            )
        if self.return_picking_id and not self.return_carrier_tracking_ref:
            raise UserError(
                _(
                    """
                    This delivery order is connected to a return. A return shipping label must be shipped
                    with the replacement part and the return tracking number recorded
                    """
                )
            )
        return super(StockPicking, self).button_validate()

    @api.constrains("sale_id")
    def _set_helpdesk_from_so(self):
        for record in self:
            if record.sale_id and not record.ticket_id and record.sale_id.ticket_id:
                record.ticket_id = record.sale_id.ticket_id

    @api.constrains("ticket_id")
    def _set_helpdesk_picking(self):
        for record in self:
            if record.ticket_id:
                record.ticket_id.picking_ids = [(4, record.id)]

    @api.onchange("ticket_id")
    def _set_helpdesk_receipt_values(self):
        if self.ticket_id:
            picking_type_id = self.env["stock.picking.type"].search(
                [("code", "=", "incoming")], limit=1
            )
            self.picking_type_id = picking_type_id
            action = {"domain": {"location_dest_id": [("return_location", "=", True)]}}
            return action

    def approve_picking(self):
        for record in self:
            if self.user_has_groups(
                "base_csi.group_delivery_order_approval"
            ) and self.env.user not in record.approval_ids.mapped("name"):
                record.env["stock.picking.approval"].create(
                    {"picking_id": record.id, "name": self.env.user.id}
                )
            else:
                raise UserError(
                    """You have already approved this picking or do not have access."""
                )

    def _approved_picking(self):
        for record in self:
            if record.picking_type_code == "outgoing":
                if (
                    len(record.approval_ids)
                    >= self.env.user.company_id.picking_approvers
                ):
                    record.approved = True
                else:
                    record.approved = False
            else:
                record.approved = True

    def action_done(self):
        res = super(StockPicking, self).action_done()
        company = self.env.user.company_id
        if self.picking_type_code == "outgoing":
            if not self.carrier_tracking_ref:
                raise UserError(
                    """Enter a tracking number in the Tracking Reference field to validate this delivery order."""
                )
            if company.auto_ss:
                if self.ss_id == 0:
                    self.create_update_ssorder()
                self.ship_ssorder()

        return res

    @api.constrains("move_lines")
    def set_calc_dimensions(self):
        for record in self:
            record.calc_dimensions()

    def calc_dimensions(self):
        for record in self:
            delivery_length = delivery_width = delivery_height = 0
            for m in record.move_lines:
                multiplier = m.product_uom_qty
                if m.quantity_done > 0:
                    multiplier = m.quantity_done
                delivery_length += record.product_id.delivery_length * multiplier
                delivery_width += record.product_id.delivery_width * multiplier
                delivery_height += record.product_id.delivery_height * multiplier
            record.write(
                {
                    "delivery_length": delivery_length,
                    "delivery_width": delivery_width,
                    "delivery_height": delivery_height,
                }
            )

    def cancel_shipstation_order(self):
        for record in self:
            if record.ss_id != 0 and record.ss_status not in ["cancelled"]:
                if record.ss_ship_id != 0:
                    record.void_sslabel()
                record.delete_ssorder()

    def action_void_sslabel(self, ss_ship_id, ss_id, return_order=False):
        company = self.env.user.company_id
        url = "%s/shipments/voidlabel" % (company.shipstation_root_endpoint)
        ship_dict = {"shipmentId": ss_ship_id}
        data_to_post = json.dumps(ship_dict)
        conn = company.shipstation_connection(url, "POST", data_to_post)
        response = conn[0]
        content = conn[1]
        if response.status_code != requests.codes.ok:
            raise UserError(_("%s\n%s: %s" % (url, response.status_code, content)))
        json_object_str = content.decode("utf-8")
        json_object = json.loads(json_object_str)
        self.message_post(body=_("<b>Shipstation</b> order <b>%s</b> %s") % (ss_id, json_object["message"]))

    def void_sslabel(self):
        for record in self:
            if not record.ss_id:
                raise UserError(
                    _("There is no shipstation order linked to this transfer.")
                )
            else:
                record.action_void_sslabel(record.ss_ship_id, record.ss_id)
            if not record.return_ss_id:
                raise UserError(
                    _("There is no shipstation order linked to this transfer.")
                )
                record.action_void_sslabel(record.return_ss_ship_id, record.return_ss_id)

    """
    @api.constrains("sale_id")
    def add_client_account_if_present(self):
        for record in self:
            if record.sale_id and record.sale_id.client_account:
                record.client_account = record.sale_id.client_account
            if record.sale_id and record.sale_id.delivery_package:
                record.delivery_package = record.sale_id.delivery_package.id
            if record.sale_id:
                record.delivery_length = record.sale_id.delivery_length
                record.delivery_width = record.sale_id.delivery_width
                record.delivery_height = record.sale_id.delivery_height
                record.confirmation = record.sale_id.confirmation
    """

    def action_delete_ssorder(self, ss_id, return_order=None):
        company = self.env.user.company_id
        url = "%s/orders/%s" % (company.shipstation_root_endpoint, ss_id)
        conn = company.shipstation_connection(url, "DELETE", False)
        response = conn[0]
        content = conn[1]
        if response.status_code != requests.codes.ok:
            raise UserError(_("%s\n%s: %s" % (url, response.status_code, content)))
        json_object_str = content.decode("utf-8")
        json_object = json.loads(json_object_str)
        if return_order:
            self.write({"return_ss_status": "cancelled"})
            self.message_post(body=_("<b>Shipstation</b> return order <b>%s</b> %s") % (ss_id, json_object["message"]))
        else:
            self.write({"ss_status": "cancelled"})
            self.message_post(body=_("<b>Shipstation</b> order <b>%s</b> %s") % (ss_id, json_object["message"]))

    def delete_ssorder(self):
        for record in self:
            if not record.ss_id:
                raise UserError(
                    _("There is no shipstation order linked to this transfer.")
                )
            else:
                record.action_delete_ssorder(record.ss_id)
            if not record.return_ss_id:
                raise UserError(
                    _("There is no return shipstation order linked to this transfer.")
                )
            else:
                record.action_delete_ssorder(record.return_ss_id, True)

    def action_cancel(self):
        if not self.is_cancel and self.env.context.get('action_button_call'):
            view = self.env.ref("base_csi.view_cancellation_warning_wizard_form")
            return {
                "name": _("Cancellation Warning"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "cancellation.warning.wizard",
                "views": [(view.id, "form")],
                "view_id": view.id,
                "target": "new",
            }
        return super(StockPicking, self).action_cancel()

    def action_ship_ssorder(self, ss_id):
        company = self.env.user.company_id
        url = "%s/orders/createlabelfororder" % (
            company.shipstation_root_endpoint
        )
        pack = "package"
        if self.delivery_package:
            pack = self.delivery_package.code
        weight = self.shipping_weight
        if weight <= 0:
            weight = 1
        if self.ss_order_weight > 0:
            weight = self.ss_order_weight
        ship_dict = {
            "orderId": ss_id,
            "carrierCode": self.carrier_id.carrier_code.carrier_code,
            "serviceCode": self.carrier_id.service_code,
            "packageCode": pack,
            "confirmation": self.confirmation,
            "shipDate": str(datetime.datetime.now()),
            "weight": {"value": weight, "units": "pounds"},
            "testLabel": False,
        }
        if (
            self.delivery_length > 0
            and self.delivery_width > 0
            and self.delivery_height > 0
        ):
            ship_dict.update(
                {
                    "dimensions": {
                        "units": "inches",
                        "length": int(self.delivery_length),
                        "width": int(self.delivery_width),
                        "height": int(self.delivery_height),
                    }
                }
            )
        data_to_post = json.dumps(ship_dict)
        conn = company.shipstation_connection(url, "POST", data_to_post)
        response = conn[0]
        content = conn[1]
        if response.status_code != requests.codes.ok:
            raise UserError(
                _("%s\n%s: %s" % (url, response.status_code, content))
            )
        json_object_str = content.decode("utf-8")
        return json.loads(json_object_str)

    def ship_ssorder(self):
        attachment_ids = []
        for record in self:
            try:
                if (
                    record.ss_id == 0
                    or not record.carrier_id
                    or not record.carrier_id.service_code
                ):
                    pass
                label_data = record.action_ship_ssorder(record.ss_id)
                self.write({
                    "ss_status": "shipped",
                    "carrier_tracking_ref": label_data["trackingNumber"]
                })
                self.message_post(body=_("<b>Shipstation</b> order shipment ID <b>%s</b> has been <b>shipped</b> via the API.\nCost: %s\nInsurance: %s\nTracking: %s") % (
                    label_data["shipmentId"], label_data["shipmentCost"], label_data["insuranceCost"], label_data["trackingNumber"]))
                attachment_id = record.sudo().output_pdf(label_data['labelData'])
                attachment_ids.append(attachment_id)
            except Exception as e:
                _logger.error("Error while processing label printing for %s" % record)
                _logger.error(e)
                pass

            # Return order
            try:
                if (
                    record.return_ss_id == 0
                    or not record.carrier_id
                    or not record.carrier_id.service_code
                ):
                    pass
                label_data = record.action_ship_ssorder(record.return_ss_id)
                self.write({
                    "return_ss_status": "shipped",
                    "return_carrier_tracking_ref": label_data["trackingNumber"]
                })
                self.message_post(body=_("<b>Shipstation</b> return order shipment ID <b>%s</b> has been <b>shipped</b> via the API.\nCost: %s\nInsurance: %s\nTracking: %s") % (
                    label_data["shipmentId"], label_data["shipmentCost"], label_data["insuranceCost"], label_data["trackingNumber"]))
                attachment_id = record.sudo().output_pdf(label_data['labelData'], True)
                attachment_ids.append(attachment_id)
            except Exception as e:
                _logger.error("Error while processing label printing for %s" % record)
                _logger.error(e)
                pass
        if attachment_ids:
            base_url = self.sudo().env["ir.config_parameter"].get_param("web.base.url")
            download_url = '/web/binary/download_document?tab_id=%s' % attachment_ids
            url = str(base_url) + str(download_url)
            return {
                "type": "ir.actions.act_url",
                "name": "ship_documents_2",
                "target": "new",
                "url": url,
            }

    def output_pdf(self, label_data, return_order=None):
        def append_pdf(input, output):
            [
                output.addPage(input.getPage(page_num))
                for page_num in range(input.numPages)
            ]

        output = PdfFileWriter()
        with open(
            os.path.expanduser("/tmp/data.pdf"), "wb"
        ) as fout:
            fout.write(base64.b64decode(label_data))
        append_pdf(
            PdfFileReader(
                open("/tmp/data.pdf", "rb"), strict=True
            ),
            output,
        )

        output.write(open("/tmp/CombinedPages.pdf", "wb"))
        output_file = open("/tmp/CombinedPages.pdf", "rb")
        output_byte = output_file.read()
        self.invoice_report = base64.encodestring(output_byte)
        self.store_fname = "ship_documents.pdf"
        if return_order:
            report_name = (
                "return ship_documents - labels" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") + ".pdf"
            )
        else:
            report_name = (
                "ship_documents - labels" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") + ".pdf"
            )
        attachment = self.env["ir.attachment"].create(
            {
                "name": "Return Shipping Documents %s" % datetime.datetime.now().strftime("%Y_%m_%d") if return_order else "Shipping Documents %s"
                % datetime.datetime.now().strftime("%Y_%m_%d"),
                "store_fname": report_name,
                "datas": base64.encodestring(output_byte),
                "res_model": "stock.picking",
                "res_id": self.id,
                "type": "binary",
                "url": "url",
                "mimetype": "application/pdf",
            }
        )
        self.env["ir.attachment"].create(
            {
                "name": "Shipping Documents %s"
                % datetime.datetime.now().strftime("%Y_%m_%d"),
                "store_fname": report_name,
                "datas": base64.encodestring(output_byte),
                "res_model": "sale.order",
                "res_id": self.id,
                "type": "binary",
                "url": "url",
                "mimetype": "application/pdf",
            }
        )
        os.remove("/tmp/data.pdf")
        os.remove("/tmp/CombinedPages.pdf")
        download_url = "/web/content/" + str(attachment.id) + "?download=True"
        base_url = self.sudo().env["ir.config_parameter"].get_param("web.base.url")
        url = str(base_url) + str(download_url)
        if return_order:
            self.return_document_url = url
        else:
            self.document_url = url
        return attachment.id

    def action_create_update_ssorder(self, company, customer, return_order=False):
        nonstandard = False
        if self.sale_id and self.sale_id.client_order_ref:
            ss_name = str(self.sale_id.client_order_ref)
        elif self.sale_id:
            ss_name = str(self.sale_id.name)
        else:
            ss_name = str(self.name)

        if return_order:
            ss_name = "Return " + ss_name
        selected_email = customer.email
        foreign = False
        if customer.country_id and customer.country_id.code != "US":
            foreign = True
        customer_object = {
            "street1": customer.street,
            "street2": customer.street2 or None,
            "city": customer.city,
            "state": customer.state_id.code,
            "postalCode": customer.zip,
            "country": customer.country_id.code,
            "phone": customer.phone or None,
            "residential": customer.residential,
        }
        if customer.parent_id:
            customer_object.update(
                {"name": customer.name, "company": customer.parent_id.name}
            )
        else:
            customer_object.update({"name": customer.name})
        url = "%s/orders/createorder" % (company.shipstation_root_endpoint)
        order_item_list = []
        sale_ids_list = []
        # qty_to_use = 0
        # HACK
        customsItems = []
        component_total = sum(
            [
                (l.product_id.standard_price * l.product_uom_qty)
                for l in self.move_lines
            ]
        )
        for p in self.move_lines:
            if p.sale_line_id:
                unit_price = p.sale_line_id.price_unit
                tax_amount = p.sale_line_id.price_reduce_taxinc
                if (
                    p.sale_line_id.product_id.bom_ids
                    and p.sale_line_id.product_id.bom_ids[0].type == "phantom"
                    and component_total > 0
                ):
                    share_component = (
                        p.product_id.standard_price * p.product_uom_qty
                    ) / component_total
                    unit_price = round(
                        p.sale_line_id.price_unit * share_component, 2
                    )
                    tax_amount = round(
                        p.sale_line_id.price_reduce_taxinc * share_component, 2
                    )
                clientref = self.sale_id.client_order_ref
                sale_ids_list.append(p.sale_line_id.id)
            else:
                unit_price = p.product_id.product_tmpl_id.list_price
                clientref = ""
                tax_amount = 0
            options_dict = [
                {"name": "Unit of Measure", "value": p.product_uom.name}
            ]
            if p.sale_line_id:
                options_dict.append(
                    {"name": "Description", "value": p.sale_line_id.name}
                )
            name_to_use = p.product_id.display_name
            if foreign:
                name_to_use = p.product_id.display_name
            newitem = {
                "lineItemKey": str(p.id),
                # "sku": p.product_id.default_code or p.product_id.name,
                "name": name_to_use,
                "taxAmount": tax_amount,
                "quantity": int(p.product_uom_qty) if not p.quantity_done else int(p.quantity_done),
                "unitPrice": unit_price,
                "upc": p.product_id.barcode or None,
                "options": options_dict,
            }
            if foreign:
                customitemdict = {
                    "description": name_to_use,
                    "quantity": int(p.product_uom_qty) if not p.quantity_done else int(p.quantity_done),
                    "value": unit_price * int(p.product_uom_qty),
                    "harmonizedTariffCode": p.product_id.tariff_code,
                    "countryOfOrigin": p.product_id.country_origin.code
                    if p.product_id.country_origin
                    else "US",
                }
                customsItems.append(customitemdict)

            order_item_list.append(newitem)

        if not company.partner_id.shipstation_warehouse_id:
            raise UserError(
                _(
                    "There is no shipstation warehouse associated to your company %s."
                    % (company.name)
                )
            )
        warehouse = company.partner_id.shipstation_warehouse_id.warehouse_id
        if self.location_dest_id.return_location:
            if not self.partner_id.shipstation_warehouse_id:
                self.partner_id.create_shipstation_warehouse_id()
            warehouse = self.partner_id.shipstation_warehouse_id.warehouse_id
        add_option = {"warehouseId": warehouse}
        if nonstandard:
            add_option.update({"customField1": "Non-Standard"})
        if self.delivery_package:
            add_option.update({"customField2": self.delivery_package.name})
        if self.client_account:
            add_option.update(
                {
                    "billToParty": "third_party",
                    "billToAccount": self.client_account.name,
                    "billToPostalCode": self.client_account.zip,
                    "billToCountryCode": self.partner_id.country_id.code
                    or "US",
                }
            )
        order_weight = p.picking_id.shipping_weight
        if self.ss_order_weight > 0:
            order_weight = self.ss_order_weight
        python_dict = {
            "orderNumber": ss_name,
            "orderKey": "Return-" + str(self.id) if return_order else str(self.id),
            "orderDate": str(datetime.datetime.now()),
            "billTo": customer_object,
            "shipTo": customer_object,
            "items": order_item_list,
            "orderStatus": self.ss_status or "awaiting_shipment",
            "customerEmail": selected_email,
            "customerNotes": clientref,
            "carrierCode": self.carrier_id.carrier_code.carrier_code,
            "serviceCode": self.carrier_id.service_code,
            "requestedShippingService": self.carrier_id.service_code,
            "confirmation": self.confirmation,
            "shipByDate": str(self.scheduled_date),
            "advancedOptions": add_option,
            "weight": {"value": order_weight, "units": "pounds"},
        }
        if foreign:
            international_add = {
                "internationalOptions": {
                    "contents": "merchandise",
                    "customsItems": customsItems,
                }
            }
            python_dict.update(international_add)
        if (
            self.delivery_package
            and self.delivery_package.created_by_shipstation
        ):
            python_dict.update({"packageCode": self.delivery_package.code})
        if (
            self.delivery_length > 0
            and self.delivery_width > 0
            and self.delivery_height > 0
        ):
            python_dict.update(
                {
                    "dimensions": {
                        "units": "inches",
                        "length": int(self.delivery_length),
                        "width": int(self.delivery_width),
                        "height": int(self.delivery_height),
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
        if self.ss_id == 0:
            self.message_post(
                body=_(
                    "<b>Shipstation</b> order <b>%s</b> has been <b>created</b> via the API."
                )
                % (json_object["orderId"])
            )
        else:
            self.message_post(
                body=_(
                    "<b>Shipstation</b> order <b>%s</b> has been <b>updated</b> via the API."
                )
                % (json_object["orderId"])
            )
        if return_order:
            self.write({
                "return_ss_status": json_object["orderStatus"],
                "return_ss_id": json_object["orderId"],
                "return_ss_address_status": json_object["shipTo"]["addressVerified"],
            })
        else:
            self.write({
                "ss_status": json_object["orderStatus"],
                "ss_id": json_object["orderId"],
                "ss_address_status": json_object["shipTo"]["addressVerified"],
            })

    def create_update_ssorder(self):
        for record in self:
            company = record.env.user.company_id
            try:
                record.action_create_update_ssorder(company, record.partner_id)
            except Exception as e:
                _logger.error(
                    "Error while processing shipstation send order for %s" % self
                )
                _logger.error(e)
                continue

            # create return order
            try:
                record.action_create_update_ssorder(company, record.picking_type_id.warehouse_id.partner_id, True)
            except Exception as e:
                _logger.error(
                    "Error while processing shipstation send order for %s" % self
                )
                _logger.error(e)
                continue


class CancellationWarning(models.TransientModel):
    _name = "cancellation.warning.wizard"
    _description = "Cancellation Warning"

    def done_cancellation(self):
        active_ids = self.env.context.get("active_ids")
        active_model = self.env.context.get("active_model")
        docs = self.env[active_model].browse(active_ids)
        docs.is_cancel = True
        docs.action_cancel()
        for record in docs:
            if record.ss_id != 0 and record.ss_status not in ["cancelled", "shipped"]:
                if record.ss_ship_id != 0:
                    record.void_sslabel()
                record.delete_ssorder()
            return True
