from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    department_id = fields.Many2one("purchase.department", string="Department")
    approver_ids = fields.One2many(
        "purchase.approver", "purchase_id", string="Pending Approvals"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("to approve", "To Approve"),
            ("1approved", "First Approval"),
            ("2approved", "Second Approval"),
            ("approved", "Approved"),
            ("approved_sent", "Sent (Approved)"),
            ("purchase", "Purchase Order"),
            ("done", "Locked"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="draft",
        track_visibility="onchange",
    )
    approver_emails = fields.Char(
        string="Approver Emails", store=True, compute="store_approver_emails"
    )
    date_approved = fields.Datetime(string="Approved Date")
    date_confirmed = fields.Datetime(string="Confirmed Date")

    def approve_order(self):
        for record in self:
            open_approvers = record.approver_ids.filtered(lambda a: a.approved is False)
            open_approvers_refined = open_approvers.filtered(
                lambda x: x.approver_id.id != record.env.user.id
            )
            self_approver = open_approvers.filtered(
                lambda x: x.approver_id.id == record.env.user.id
            )
            if self_approver and (
                len(open_approvers_refined) == 1
                or all(l.stage > self_approver.stage for l in open_approvers_refined)
            ):
                record.message_post(
                    body=_("Purchase Approved by %s") % record.env.user.name
                )
                app_id = record.approver_ids.filtered(
                    lambda a: a.approver_id.id == record.env.user.id
                )
                app_id.write({"approved": True})
                if (
                    len(record.approver_ids.filtered(lambda a: a.approved is False))
                    == 0
                ):
                    record.state = "approved"
                    record.date_approved = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    record.message_post(
                        body=_("Purchase Has Been Approved by All Parties")
                    )
                else:
                    if app_id.stage == 1:
                        record.state = "1approved"
                    if app_id.stage == 2:
                        record.state = "2approved"
            elif record.env.user.has_group("base_csi.group_exec_mgmt"):
                wiz_context = {
                    "default_purchase_id": record.id,
                    "personnel": record.approver_ids.filtered(lambda x: not x.approved)
                    .mapped("approver_id")
                    .filtered(lambda x: x.id != record.env.user.id)
                    .ids,
                }
                action_data = record.env.ref(
                    "base_csi.action_purchase_order_approval_behalf"
                ).read()[0]
                action_data.update({"context": wiz_context})
                return action_data
            elif self_approver and any(
                l.stage < self_approver.stage for l in open_approvers_refined
            ):
                raise UserError(
                    _(
                        "The previous layer of approval must be approved before approving this one."
                    )
                )
            else:
                raise UserError(
                    _(
                        """You have already approved this order
                        or do not have the appropriate access level
                        to approve on other personnel's behalf."""
                    )
                )

    def submit_for_approval(self):
        for record in self:

            def get_amount_by_currency(amount):
                return record.env.user.company_id.currency_id.compute(
                    amount, record.currency_id
                )

            po_amount = record.amount_total
            if len(record.company_id.threshold_ids) == 0:
                raise UserError(
                    _("Approval thresholds are not configured for the company.")
                )
            elif len(record.approver_ids) == 0:
                wiz_context = {
                    "default_purchase_id": record.id,
                    "default_template_id": record.env.ref(
                        "base_csi.mail_template_purchase_approval"
                    ).id,
                }

                approver_count = 0

                for threshold in record.company_id.threshold_ids:
                    min_threshold = get_amount_by_currency(threshold.min_amount)
                    if po_amount >= min_threshold:
                        approver_count = threshold.approver_num
                    else:
                        break

                pre_authorized = (
                    record.env["purchase.user.approval.threshold"]
                    .search(
                        [
                            ("account_id", "in", [record.department_id.id]),
                            ("max_amount", ">=", po_amount),
                        ]
                    )
                    .mapped("user_id")
                )
                exec_team = record.env["res.users"].search(
                    [
                        (
                            "groups_id",
                            "in",
                            [record.env.ref("base_csi.group_exec_mgmt").id],
                        )
                    ]
                )
                authorized = pre_authorized | exec_team
                authorized = authorized.filtered(lambda x: x.id != record.env.user.id)

                if len(authorized) < approver_count:
                    raise UserError(
                        _(
                            """Not enough people in the company
                            are authorized to approve this order.
                            Please check user configuration."""
                        )
                    )

                if approver_count == 1:
                    wiz_context.update(
                        {"threshold1": True, "authorized": authorized.ids}
                    )
                elif approver_count == 2:
                    wiz_context.update(
                        {
                            "threshold1": True,
                            "threshold2": True,
                            "authorized": authorized.ids,
                        }
                    )
                elif approver_count == 3:
                    wiz_context.update(
                        {
                            "threshold1": True,
                            "threshold2": True,
                            "authorized": authorized.ids,
                            "threshold3": True,
                        }
                    )
                if approver_count > 0:
                    action_data = record.env.ref(
                        "base_csi.action_purchase_order_approval"
                    ).read()[0]
                    action_data.update({"context": wiz_context})
                    return action_data
                else:
                    record.state = "approved"
            else:
                record.approver_ids.unlink()

    def batch_approve_order(self):
        for record in self:
            open_approvers = record.approver_ids.filtered(lambda a: a.approved is False)
            open_approvers_refined = open_approvers.filtered(
                lambda x: x.approver_id.id != record.env.user.id
            )
            self_approver = open_approvers.filtered(
                lambda x: x.approver_id.id == record.env.user.id
            )
            if self_approver and (
                len(open_approvers_refined) == 1
                or all(l.stage > self_approver.stage for l in open_approvers_refined)
            ):
                record.message_post(
                    body=_("Purchase Approved by %s") % record.env.user.name
                )
                app_id = record.approver_ids.filtered(
                    lambda a: a.approver_id.id == record.env.user.id
                )
                app_id.write({"approved": True})
                if (
                    len(record.approver_ids.filtered(lambda a: a.approved is False))
                    == 0
                ):
                    record.state = "approved"
                    record.date_approved = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    record.message_post(
                        body=_("Purchase Has Been Approved by All Parties")
                    )
                else:
                    if app_id.stage == 1:
                        record.state = "1approved"
                    if app_id.stage == 2:
                        record.state = "2approved"
            elif record.env.user.has_group("base_csi.group_exec_mgmt"):
                to_approve_for = (
                    record.approver_ids.filtered(lambda x: not x.approved)
                    .mapped("approver_id")
                    .filtered(lambda x: x.id != record.env.user.id)
                )
                approver_id = to_approve_for[0]
                record.message_post(
                    body=_("Purchase Approved by %s on Behalf of %s")
                    % (record.env.user.name, approver_id.name)
                )
                app_id = record.approver_ids.filtered(
                    lambda a: a.approver_id.id == approver_id.id
                )
                app_id.write({"approved": True})
                if (
                    len(record.approver_ids.filtered(lambda a: a.approved is False))
                    == 0
                ):
                    record.state = "approved"
                    record.date_approved = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    record.message_post(
                        body=_("Purchase Has Been Approved by All Parties")
                    )
                else:
                    if app_id.stage == 1:
                        record.state = "1approved"
                    if app_id.stage == 2:
                        record.state = "2approved"
            elif self_approver and any(
                l.stage < self_approver.stage for l in open_approvers_refined
            ):
                continue
            else:
                continue

    def batch_submit_approval(self):
        for record in self:

            def get_amount_by_currency(amount):
                return record.env.user.company_id.currency_id.compute(
                    amount, record.currency_id
                )

            po_amount = record.amount_total
            if len(record.company_id.threshold_ids) == 0:
                continue
            if record.approver_ids:
                continue
            template = record.env.ref("base_csi.mail_template_purchase_approval").id
            approver_count = 0

            for threshold in record.company_id.threshold_ids:
                min_threshold = get_amount_by_currency(threshold.min_amount)
                if po_amount >= min_threshold:
                    approver_count = threshold.approver_num
                else:
                    break

            pre_authorized = (
                record.env["purchase.user.approval.threshold"]
                .search(
                    [
                        ("account_id", "in", [record.department_id.id]),
                        ("max_amount", ">=", po_amount),
                    ]
                )
                .mapped("user_id")
            )
            exec_team = record.env["res.users"].search(
                [("groups_id", "in", [record.env.ref("base_csi.group_exec_mgmt").id])]
            )
            authorized = pre_authorized | exec_team
            authorized = authorized.filtered(lambda x: x.id != record.env.user.id)

            if len(authorized) < approver_count:
                continue

            record.approver_ids.create(
                {
                    "approver_id": authorized[0].id,
                    "approved": False,
                    "purchase_id": record.id,
                    "stage": 1,
                }
            )
            if approver_count == 2:
                record.approver_ids.create(
                    {
                        "approver_id": authorized[1].id,
                        "approved": False,
                        "purchase_id": record.id,
                        "stage": 1,
                    }
                )
            if approver_count == 3:
                record.approver_ids.create(
                    {
                        "approver_id": authorized[2].id,
                        "approved": False,
                        "purchase_id": record.id,
                        "stage": 1,
                    }
                )
            record.state = "to approve"
            record.message_post_with_template(template)

    @api.depends("approver_ids")
    def store_approver_emails(self):
        for record in self:
            record.approver_emails = False
            if record.approver_ids:
                results = list(
                    map(
                        str,
                        record.approver_ids.mapped("approver_id")
                        .mapped("partner_id")
                        .ids,
                    )
                )
                record.approver_emails = ",".join(results)

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get("mark_rfq_as_sent"):
            self.filtered(lambda o: o.state == "draft").write({"state": "sent"})
            self.filtered(lambda o: o.state == "approved").write(
                {"state": "approved_sent"}
            )
        return super(
            PurchaseOrder, self.with_context(mail_post_autofollow=False)
        ).message_post(**kwargs)

    def print_quotation(self):
        return self.env.ref("purchase.report_purchase_quotation").report_action(self)

    def button_confirm(self):
        for order in self:
            if order.state not in ["approved", "approved_sent"]:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if (
                order.company_id.po_double_validation == "one_step"
                or (
                    order.company_id.po_double_validation == "two_step"
                    and order.amount_total
                    < self.env.user.company_id.currency_id.compute(
                        order.company_id.po_double_validation_amount, order.currency_id
                    )
                )
                or order.user_has_groups("purchase.group_purchase_manager")
            ):
                order.button_approve()
                order.date_confirmed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                order.write({"state": "to approve"})
        return True


class PurchaseDepartment(models.Model):
    _name = "purchase.department"
    _description = "Departments"
    _order = "name desc"

    name = fields.Char(string="Dept. Name")


class PurchaseApprover(models.Model):
    _name = "purchase.approver"
    _description = "Purchase Approver"

    approved = fields.Boolean(string="Approved")
    approver_id = fields.Many2one("res.users", string="Approver")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")
    stage = fields.Integer(string="Approval Stage")


class PurchaseApprovalThreshold(models.Model):
    _name = "purchase.approval.threshold"
    _description = "Purchase Approval Threshold"
    _order = "min_amount"

    min_amount = fields.Float(string="Min. Amount")
    company_id = fields.Many2one("res.company", string="Company")
    approver_num = fields.Integer(string="Num. of Approvers (3 Max)")


class PurchaseUserApprovalThreshold(models.Model):
    _name = "purchase.user.approval.threshold"
    _description = "Purchase User Approval Thresholds"
    _order = "max_amount"

    max_amount = fields.Float(string="Max. Amount")
    user_id = fields.Many2one("res.users", string="User")
    account_id = fields.Many2one("purchase.department", string="Department")


class PurchaseApprovalWizard(models.TransientModel):
    _name = "purchase.approval.wizard"
    _description = "Purchase Approval Wizard"

    approver_one_id = fields.Many2one("res.users", string="First Approval")
    approver_two_id = fields.Many2one("res.users", string="Second Approval")
    approver_three_id = fields.Many2one("res.users", string="Third Approval")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")
    template_id = fields.Many2one("mail.template", string="Email Template")

    def submit_approval(self):
        for record in self:
            if record.purchase_id:
                approvers = record.env["res.users"]
                if record.approver_one_id:
                    approvers |= record.approver_one_id
                    record.purchase_id.approver_ids.create(
                        {
                            "approver_id": record.approver_one_id.id,
                            "approved": False,
                            "purchase_id": record.purchase_id.id,
                            "stage": 1,
                        }
                    )
                if record.approver_two_id:
                    approvers |= record.approver_two_id
                    record.purchase_id.approver_ids.create(
                        {
                            "approver_id": record.approver_two_id.id,
                            "approved": False,
                            "purchase_id": record.purchase_id.id,
                            "stage": 2,
                        }
                    )
                if record.approver_three_id:
                    approvers |= record.approver_three_id
                    record.purchase_id.approver_ids.create(
                        {
                            "approver_id": record.approver_three_id.id,
                            "approved": False,
                            "purchase_id": record.purchase_id.id,
                            "stage": 3,
                        }
                    )
                record.purchase_id.state = "to approve"
                record.purchase_id.message_post_with_template(record.template_id.id)


class PurchaseApprovalBehalfWizard(models.TransientModel):
    _name = "purchase.approval.behalf.wizard"
    _description = "Purchase Approval Behalf Wizard"

    approver_id = fields.Many2one("res.users", string="Approver")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")

    def approve_on_behalf(self):
        for record in self:
            if (
                record.env.user.has_group("base_csi.group_exec_mgmt")
                and record.approver_id
            ):
                open_approvers = record.purchase_id.approver_ids.filtered(
                    lambda a: a.approved is False
                    and a.approver_id.id != record.approver_id.id
                )
                self_approver = record.purchase_id.approver_ids.filtered(
                    lambda a: a.approved is False
                    and a.approver_id.id == record.approver_id.id
                )
                if open_approvers and any(
                    l.stage < self_approver.stage for l in open_approvers
                ):
                    raise UserError(
                        _(
                            """You can't approve for this user yet,
                            earlier stages of the approval process
                            have not been completed."""
                        )
                    )
                record.purchase_id.message_post(
                    body=_("Purchase Approved by %s on Behalf of %s")
                    % (record.env.user.name, record.approver_id.name)
                )
                app_id = record.purchase_id.approver_ids.filtered(
                    lambda a: a.approver_id.id == record.approver_id.id
                )
                app_id.write({"approved": True})
                if (
                    len(
                        record.purchase_id.approver_ids.filtered(
                            lambda a: a.approved is False
                        )
                    )
                    == 0
                ):
                    record.purchase_id.state = "approved"
                    record.purchase_id.date_approved = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    record.purchase_id.message_post(
                        body=_("Purchase Has Been Approved by All Parties")
                    )
                else:
                    if app_id.stage == 1:
                        record.purchase_id.state = "1approved"
                    if app_id.stage == 2:
                        record.purchase_id.state = "2approved"
            else:
                raise UserError(
                    _(
                        "Missing approver and/or you do not have the authority to approve on someone else's behalf."
                    )
                )
