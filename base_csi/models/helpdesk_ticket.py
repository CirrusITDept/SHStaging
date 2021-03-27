# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MailMessage(models.Model):
    _inherit = "mail.message"

    salesforce_id = fields.Char(string="Salesforce ID")


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    salesforce_id = fields.Char(string="Salesforce ID")


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    projected_install_date = fields.Date(string="Projected Install Date", copy=False, store=True)
    helpdesk_team_name = fields.Char(related="team_id.name")
    partner_end_id = fields.Many2one("res.partner", string="End User")
    partner_sign_id = fields.Many2one("res.partner", string="Sign Shop")
    partner_dist_id = fields.Many2one("res.partner", string="Distributor")
    partner_phone = fields.Char(string="Customer Phone")
    salesforce_id = fields.Char(string="Salesforce ID")
    salesforce_case_number = fields.Char(string="Salesforce Case #")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    next_action = fields.Html(string="Next Action")
    display_id = fields.Many2one("display.display", string="Display")
    sale_id = fields.Many2one("sale.order", string="Sale Order")
    sale_ids = fields.One2many("sale.order", "ticket_id", string="Created Sale Orders")
    alert_ids = fields.One2many("quality.alert", "ticket_id", string="Quality Alerts")
    sale_count = fields.Integer(string="Sale Count", compute="_get_record_counts")
    alert_count = fields.Integer(string="Alert Count", compute="_get_record_counts")
    salesforce_order_count = fields.Integer(
        string="Order Count", compute="_get_record_counts"
    )
    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sales Order",
        related="sale_id",
        store=True,
        domain="[('partner_id', 'child_of', commercial_partner_id), ('company_id', '=', company_id)]",
    )
    salesforce_order = fields.Many2one("salesforce.order", string="Salesforce Order")
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        store="True",
        related="product_id.product_tmpl_id",
    )
    internal_description = fields.Text(string="Internal Description")
    days_since_last_activity = fields.Integer(string="Inactive Days", compute='_inactive_days', store=True)
    previous_days_since_last_activity = fields.Integer(string="Previous Inactive Days", readonly=True)

    @api.constrains("display_id")
    def set_helpdesk_id(self):
        self.display_id.helpdesk_id = self.id

    @api.depends('write_date', 'message_ids.create_date')
    def _inactive_days(self):
        for rec in self:
            most_recent_date = []
            if not rec.stage_id.is_close:
                if rec.message_ids:
                    most_recent_date.append(rec.message_ids[0].create_date)
                most_recent_date.append(rec.write_date)
                max_most_recent_date = max(most_recent_date)
                if max_most_recent_date:
                    today = fields.datetime.today()
                    rec.days_since_last_activity = (today - max_most_recent_date).days
                    if rec.days_since_last_activity != 0:
                        rec.previous_days_since_last_activity = (today - max_most_recent_date).days

    @api.depends("picking_ids")
    def _compute_pickings_count(self):
        for ticket in self:
            ticket.pickings_count = len(
                ticket.picking_ids.filtered(
                    lambda b: b.picking_type_id.code == "incoming"
                )
            )

    def action_view_pickings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Return Orders"),
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [
                ("id", "in", self.picking_ids.ids),
                ("picking_type_id.code", "=", "incoming"),
            ],
            "context": dict(
                self._context, create=False, default_company_id=self.company_id.id
            ),
        }

    @api.onchange("sale_order_id")
    def set_order_info_on_tix(self):
        for record in self:
            if record.sale_order_id:
                record.write(
                    {
                        "partner_sign_id": record.sale_order_id.partner_sign_id.id,
                        "partner_end_id": record.sale_order_id.partner_end_id.id,
                        "partner_dist_id": record.sale_order_id.partner_dist_id.id,
                    }
                )

    def open_salesforce_order(self):
        self.ensure_one()
        action = self.env.ref("base_csi.action_window_salesforce_order").read()[0]
        action["context"] = {
            "default_ticket_id": self.id,
        }
        orders = self.env["salesforce.order"].search([("ticket_id", "=", self.id)])
        orders |= self.salesforce_order
        action["domain"] = [("id", "in", orders.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if len(orders) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = orders.id
        return action

    def _get_record_counts(self):
        for record in self:
            saleorders = self.env["sale.order"]
            saleorders |= record.sale_id
            saleorders |= record.sale_ids
            record.sale_count = len(saleorders)
            record.alert_count = len(record.alert_ids)
            salesforce_order = record.env["salesforce.order"].search(
                [("ticket_id", "=", self.id)]
            )
            salesforce_order |= record.salesforce_order
            record.salesforce_order_count = len(salesforce_order)

    def button_quality_alert(self):
        self.ensure_one()
        action = self.env.ref("quality_control.quality_alert_action_check").read()[0]
        action["views"] = [(False, "form")]
        action["context"] = {
            "default_ticket_id": self.id,
            "default_display_id": self.display_id.id,
            "default_sale_id": self.sale_order_id.id,
            "default_salesforce_order": self.salesforce_order.id,
            "default_product_tmpl_id": self.product_id.product_tmpl_id.id,
            "default_product_id": self.product_id.id,
            "default_lot_id": self.lot_id.id,
        }
        return action

    def open_quality_alert(self):
        self.ensure_one()
        action = self.env.ref("quality_control.quality_alert_action_check").read()[0]
        action["context"] = {
            "default_ticket_id": self.id,
        }
        action["domain"] = [("id", "in", self.alert_ids.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if self.alert_count == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = self.alert_ids.id
        return action

    def button_sale(self):
        self.ensure_one()
        action = self.env.ref("sale.action_quotations_with_onboarding").read()[0]
        action["views"] = [(False, "form")]
        action["context"] = {
            "default_ticket_id": self.id,
            "default_partner_id": self.partner_id.id,
            "default_partner_sign_id": self.partner_sign_id.id,
            "default_partner_end_id": self.partner_end_id.id,
            "default_partner_dist_id": self.partner_dist_id.id,
            "default_display_id": self.display_id.id,
        }
        return action

    def open_sale(self):
        self.ensure_one()
        action = self.env.ref("sale.action_quotations_with_onboarding").read()[0]
        action["context"] = {
            "default_ticket_id": self.id,
            "default_partner_id": self.partner_id.id,
            "default_partner_sign_id": self.partner_sign_id.id,
            "default_partner_end_id": self.partner_end_id.id,
            "default_partner_dist_id": self.partner_dist_id.id,
        }
        orders = self.sale_id
        orders |= self.sale_ids
        action["domain"] = [("id", "in", orders.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if self.sale_count == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = orders.id
        return action

    @api.constrains("partner_id")
    def set_details(self):
        for record in self:
            if record.partner_id:
                record.partner_name = record.partner_id.name
                record.partner_phone = record.partner_id.phone
                record.partner_email = record.partner_id.email
            else:
                record.partner_name = False
                record.partner_phone = False
                record.partner_email = False

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email
            self.partner_phone = self.partner_id.phone
