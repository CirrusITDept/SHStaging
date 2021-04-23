# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmLeadReportType(models.Model):
    _name = "crm.lead.report.type"
    _description = "Repord Types"

    name = fields.Char(string="Name")


class CrmTeam(models.Model):
    _inherit = "crm.team"

    salesforce_id = fields.Char(string="Salesforce ID")


class CrmStage(models.Model):
    _inherit = "crm.stage"

    restrict_stage_change = fields.Selection(
        [
            ("none", "Nobody"),
            ("sales", "Sales Managers"),
            ("accounting", "Accounting Managers"),
        ],
        string="Restrict stage exit",
        default="none",
    )
    restrict_stage_change_into = fields.Selection(
        [
            ("none", "Nobody"),
            ("sales", "Sales Managers"),
            ("accounting", "Accounting Managers"),
        ],
        string="Restrict stage entrance",
        default="none",
    )


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_new_quotation(self):
        action = self.env.ref("sale_crm.sale_action_quotations_new").read()[0]
        action["context"] = {
            "search_default_opportunity_id": self.id,
            "default_opportunity_id": self.id,
            "search_default_partner_id": self.partner_id.id,
            "default_partner_id": self.partner_id.id,
            "default_team_id": self.team_id.id,
            "default_campaign_id": self.campaign_id.id,
            "default_medium_id": self.medium_id.id,
            "default_origin": self.name,
            "default_name": self.name,
            "default_source_id": self.source_id.id,
            "default_payment_term_id": self.payment_term_id.id or False,
            "default_display_id": self.display_id.id or False,
            "default_partner_sign_id": self.partner_sign_id.id or False,
            "default_partner_dist_id": self.partner_dist_id.id or False,
            "default_company_id": self.company_id.id or self.env.company.id,
        }
        return action

    def _get_default_closing(self):
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.use_quotation_validity_days")
        ):
            days = self.env.user.company_id.quotation_validity_days
            if days > 0:
                return fields.Date.to_string(datetime.now() + timedelta(days))
        return False

    date_deadline = fields.Date(
        "Expected Closing",
        help="Estimate of the date on which the opportunity will be won.",
        default=_get_default_closing,
    )
    end_user = fields.Many2one("res.partner", string="End User")
    partner_sign_id = fields.Many2one("res.partner", string="Sign Shop")
    partner_dist_id = fields.Many2one("res.partner", string="Distributor")
    partner_ent_acc_id = fields.Many2one("res.partner", string="Enterprise")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Method")
    dest_state_id = fields.Many2one("res.country.state", string="Dest. State")
    report_type_id = fields.Many2one("crm.lead.report.type", string="Record Type")
    salesforce_id = fields.Char(string="Salesforce ID")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    display_id = fields.Many2one("display.display", string="Display")
    salesforce_quote_count = fields.Integer(
        string="Quote Count", compute="_get_record_counts"
    )
    salesforce_order_count = fields.Integer(
        string="Order Count", compute="_get_record_counts"
    )
    opp_channel_id = fields.Selection(
        [
            ("automotive", "Automotive"),
            ("bank_realestate", "Banks/Real Estate"),
            ("billboard", "Billboard/Advertiser"),
            ("church", "Church"),
            ("entertainment", "Entertainment - Theater/Casino/Park"),
            ("gas_station", "Gas station/Convenience"),
            ("government", "Government"),
            ("healthcare", "Healthcare"),
            ("hotels", "Hotels/Hospitality"),
            ("lawyer", "Lawyer/Insurance/Etc."),
            ("municipality", "Municipality"),
            ("retail", "Retail"),
            ("rest_franchise", "Restaurant - QSR/Franchise"),
            ("rest_independent", "Restaurant - Independent"),
            ("school", "School"),
            ("sports", "Sports"),
            ("services", "Services/Other"),
            ("other", "Other"),
        ],
        string="Channel",
    )
    eu_phone_id = fields.Boolean("EU Phone Call/Software", track_visibility="onchange") 
    eu_demo_id = fields.Boolean("EU Demo Truck Visit", track_visibility="onchange")
    smb_lead_id = fields.Boolean("SMB Lead")
    channel_type_id = fields.Selection(
        [("sign_shop", "Sign Shop"), ("sbm", "SMB"), ("enterprise", "Enterprise")],
        string="Channel Type",
    )
    computed_ave_quotes = fields.Float(string="Computed Ave of Quotes", default=0.0,)

    def _convert_opportunity_data(self, customer, team_id=False):
        leads = super(CrmLead, self)._convert_opportunity_data(customer, team_id=False)
        self.smb_lead_id = True
        return leads

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        res = super(CrmLead, self)._onchange_partner_id()
        if self.partner_id:
            partner = self.partner_id
            parent_partner = self.partner_id.parent_id
            if partner.sign_shop:
                self.partner_sign_id = partner.id
            elif parent_partner and parent_partner.sign_shop:
                self.partner_sign_id = parent_partner.id
            else:
                self.partner_sign_id = False

            if partner.enterprise_account:
                self.partner_ent_acc_id = partner.id
            elif parent_partner and parent_partner.enterprise_account:
                self.partner_ent_acc_id = parent_partner.id
            else:
                self.partner_ent_acc_id = False
        return res

    def write(self, values):
        for record in self:
            if "stage_id" in values:
                stage_into = self.env["crm.stage"].browse([values["stage_id"]])
                if (
                    record.stage_id.restrict_stage_change == "sales"
                    or stage_into.restrict_stage_change_into == "sales"
                ) and not self.user_has_groups("sales_team.group_sale_manager"):
                    raise UserError(
                        "This opportunity's stage may be only moved by a Sales Manager."
                    )
                if (
                    record.stage_id.restrict_stage_change == "accounting"
                    or stage_into.restrict_stage_change_into == "accounting"
                ) and not self.user_has_groups("account.group_account_manager"):
                    raise UserError(
                        "This opportunity's stage may be only moved by a Accounting Manager."
                    )
        return super(CrmLead, self).write(values)

    def _get_record_counts(self):
        for record in self:
            record.salesforce_quote_count = record.env["salesforce.quote"].search_count(
                [("opportunityid", "=", record.id)]
            )
            record.salesforce_order_count = record.env["salesforce.order"].search_count(
                [("opportunity_id", "=", self.id)]
            )

    def open_salesforce_order(self):
        self.ensure_one()
        action = self.env.ref("base_csi.action_window_salesforce_order").read()[0]
        action["context"] = {
            "default_opportunity_id": self.id,
        }
        orders = self.env["salesforce.order"].search([("opportunity_id", "=", self.id)])
        action["domain"] = [("id", "in", orders.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if len(orders) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = orders.id
        return action

    def open_salesforce_quote(self):
        self.ensure_one()
        action = self.env.ref("base_csi.action_window_salesforce_quote").read()[0]
        action["context"] = {
            "default_opportunityid": self.id,
        }
        quotes = self.env["salesforce.quote"].search([("opportunityid", "=", self.id)])
        action["domain"] = [("id", "in", quotes.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if len(quotes) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = quotes.id
        return action

    def action_update_leads(self):
        for record in self:
            if record.partner_id:
                partner = record.partner_id
                parent_partner = record.partner_id.parent_id
                if partner.sign_shop:
                    record.partner_sign_id = partner.id
                elif parent_partner and parent_partner.sign_shop:
                    record.partner_sign_id = parent_partner.id
                else:
                    record.partner_sign_id = False

                if partner.enterprise_account:
                    record.partner_ent_acc_id = partner.id
                elif parent_partner and parent_partner.enterprise_account:
                    record.partner_ent_acc_id = parent_partner.id
                else:
                    record.partner_ent_acc_id = False


class CrmLeadLost(models.TransientModel):
    _inherit = "crm.lead.lost"

    def action_lost_reason_apply(self):
        leads = self.env["crm.lead"].browse(self.env.context.get("active_ids"))
        lost_stage_id = (
            self.env["ir.config_parameter"].sudo().get_param("base_csi.lost_stage_id")
        )
        if lost_stage_id:
            return leads.write(
                {"stage_id": int(lost_stage_id), "active": False, "probability": 0}
            )
        return leads.action_set_lost(lost_reason=self.lost_reason_id.id)
