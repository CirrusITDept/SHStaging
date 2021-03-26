# -*- coding: utf-8 -*-
import base64
from datetime import datetime
from odoo import api, models, fields


class SignSendRequest(models.TransientModel):
    _inherit = "sign.send.request"

    display_id = fields.Many2one("display.display", string="Display")

    def create_request(self, send=True, without_mail=False):
        request_info = super(SignSendRequest, self).create_request(send, without_mail)
        request_id = request_info["id"]
        if self.display_id:
            request = self.env["sign.request"].browse(request_id)
            request.display_id = self.display_id
        return request_info


class SignRequest(models.Model):
    _inherit = "sign.request"

    sale_id = fields.Many2one(
        "sale.order", string="Sale Order", store=True, related="template_id.sale_id"
    )
    display_id = fields.Many2one("display.display", string="Display")

    @api.constrains("state")
    def write_on_sale(self):
        for record in self.sudo():
            if record.sale_id and record.state == "signed":
                message = "Sign Request %s (%s) has been signed by all parties" % (
                    record.display_name,
                    record.id,
                )
                record.sale_id.sudo().message_post(body=message)
                if not record.completed_document:
                    record.generate_completed_document()
                record.env["ir.attachment"].sudo().create(
                    {
                        "name": "%s.pdf" % record.reference,
                        "datas": record.completed_document,
                        "type": "binary",
                        "res_model": "sale.order",
                        "res_id": record.sale_id.id,
                    }
                )
                report_action = self.env.ref("sign.action_sign_request_print_logs")
                public_user = self.env.ref("base.public_user", raise_if_not_found=False)
                if not public_user:
                    public_user = self.env.use
                pdf_content, __ = (
                    report_action.with_user(public_user).sudo().render_qweb_pdf(self.id)
                )
                self.env["ir.attachment"].sudo().create(
                    {
                        "name": "Activity Logs - %s.pdf"
                        % datetime.now().strftime("%Y_%m_%d"),
                        "datas": base64.b64encode(pdf_content),
                        "type": "binary",
                        "res_model": "sale.order",
                        "res_id": record.sale_id.id,
                    }
                )

class SignItem(models.Model):
    _inherit = "sign.item"

    contact_info_type = fields.Selection([
        ('busi_name', 'Business Name'),
        ('cont_name', 'Contact Name'),
        ('last_name', 'Last Name'),
        ('cont_phone', 'Phone'),
        ('cont_email', 'Email'),
        ('cont_address', 'Address'),
        ('cont_city', 'City'),
        ('cont_state', 'State'),
        ('cont_zip', 'Zip'),
        ('sale_projected_install_date', 'Anticipated Installation Date')
    ], string="Contact Info Type", help="Technical field to create contact partner")
