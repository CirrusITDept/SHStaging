# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import UserError
import requests
import logging
import json
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    salesforce_id = fields.Char(
        string="Salesforce ID", inherited=True, readonly=False, store=True
    )
    threshold_ids = fields.One2many(
        "purchase.user.approval.threshold", "user_id", string="Thresholds"
    )

    def _update_hoopla_metrics(self):
        for record in self:
            company = self.env.user.company_id
            access_token = company.hoopla_access_token
            if not access_token or not company.hoopla_team_id:
                raise UserError(
                    "To integrate with Hoopla you must have an access token assigned. Please retrieve a token by going to general settings configuration."
                )
            auth_token = "Bearer " + access_token
            headers = {
                "authorization": auth_token,
                "Content-type": "application/vnd.hoopla.metric-value+json",
            }

            user_url = "https://api.hoopla.net/users"
            params = {"email": record.login}
            r = requests.get(user_url, params=params, headers=headers)
            user_dict = json.loads(r.content)
            if not user_dict:
                _logger.error(
                    "Skipped %s since they are currently not configured in Hoopla."
                    % (record.login)
                )
                continue
            metrics_url = "https://api.hoopla.net/metrics"
            r = requests.get(metrics_url, headers=headers)
            res_dict = json.loads(r.content)

            today = fields.Datetime.today()
            first_day_of_the_month = today.replace(day=1)
            first_day_of_next_month = first_day_of_the_month + relativedelta(months=1)
            beginning_of_year = today.replace(day=1, month=1)
            end_of_year = today.replace(day=31, month=12)
            user_sos = record.env["sale.order"].search(
                [
                    ("user_id", "=", record.id),
                    ("opportunity_id", "!=", False),
                    ("opportunity_id.channel_type_id", "!=", company.hoopla_team_id,),
                    ("state", "in", ["done", "sale"]),
                ]
            )
            user_opps = record.env["crm.lead"].search(
                [
                    ("user_id", "=", record.id),
                    ("type", "=", "opportunity"),
                    ("create_date", "<", first_day_of_next_month),
                    ("create_date", ">=", first_day_of_the_month),
                ]
            )

            so_mtd = user_sos.filtered(
                lambda b: b.date_order < first_day_of_next_month
                and b.date_order >= first_day_of_the_month
            )
            so_ytd = user_sos.filtered(
                lambda b: b.date_order <= end_of_year
                and b.date_order >= beginning_of_year
            )

            metrics = [
                "Displays Sold MTD",
                "Opps Created MTD",
                "New Opps Value MTD",
                "Revenue MTD",
                "Revenue YTD",
                "Displays Sold YTD",
            ]
            metric_list = [d for d in res_dict if d["name"] in metrics]
            for metric in metric_list:
                metric_value_url = [
                    d for d in metric["links"] if d["rel"] == "list_metric_values"
                ][0]["href"]
                params = {"owner.href": user_dict[0]["href"]}
                r = requests.get(metric_value_url, params=params, headers=headers)
                metric_value_dict = json.loads(r.content)
                data = metric_value_dict[0]

                if metric["name"] == "Displays Sold MTD":
                    value = len(so_mtd)
                    data.update({"value": value})
                elif metric["name"] == "Opps Created MTD":
                    value = len(user_opps)
                    data.update({"value": value})
                elif metric["name"] == "New Opps Value MTD":
                    value = sum(user_opps.mapped("computed_ave_quotes"))
                    data.update({"value": value})
                elif metric["name"] == "Revenue MTD":
                    value = sum(so_mtd.mapped("amount_total"))
                    data.update({"value": value})
                elif metric["name"] == "Displays Sold YTD":
                    value = len(so_ytd)
                    data.update({"value": value})
                elif metric["name"] == "Revenue YTD":
                    value = sum(so_ytd.mapped("amount_total"))
                    data.update({"value": value})

                update_url = data["href"]
                data = json.dumps(data)
                r = requests.put(update_url, data=data, headers=headers)
            _logger.info("%s has been updated in Hoopla" % (record.login))
