# -*- coding: utf-8 -*-

from odoo import fields, models


class QualityAlert(models.Model):
    _inherit = "quality.alert"

    salesforce_id = fields.Char(string="Salesforce ID")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    salesforce_order = fields.Many2one("salesforce.order", string="Salesforce Order")
    display_id = fields.Many2one("display.display", string="Display")
    sale_id = fields.Many2one("sale.order", string="Sale Order")
    ticket_id = fields.Many2one("helpdesk.ticket", string="Helpdesk Ticket")
    car_completed = fields.Boolean(string="CAR Completed")
    component_faults = fields.Selection(
        [
            ("Cable Failure", "Cable Failure"),
            ("EnGenius / PoE Failure", "EnGenius / PoE Failure"),
            ("Power Injector Failure", "Power Injector Failure"),
            ("TP-Link / PoE Failure", "TP-Link / PoE Failure"),
            ("Cirrus Sight Camera Failure", "Cirrus Sight Camera Failure"),
            ("Other", "Other"),
        ],
        string="Component Faults",
    )
    controller_faults = fields.Selection(
        [
            ("Hard drive failure", "Hard drive failure"),
            ("Motherboard failure", "Motherboard failure"),
            ("Power supply failure", "Power supply failure"),
            ("Video card failure", "Video card failure"),
            ("Other", "Other"),
        ],
        string="Controller Faults",
    )
    controller_id_number = fields.Char(string="Controller ID")
    disposition_instructions_if_applicable = fields.Html(
        string="Disposition Instructions (if applicable)"
    )
    disposition_options = fields.Many2many(
        "quality.disposition.option", string="Disposition Options"
    )
    known_problems_for_controllers = fields.Selection(
        [
            ("Bad Motherboard Power Connection", "Bad Motherboard Power Connection"),
            ("Hard Drive Failure", "Hard Drive Failure"),
            ("Video Card Failure", "Video Card Failure"),
            ("Cellular Modem Failure", "Cellular Modem Failure"),
            ("Motherboard Failure", "Motherboard Failure"),
            ("Power Supply Failure", "Power Supply Failure"),
            ("Wi-Fi Card Failure", "Wi-Fi Card Failure"),
        ],
        string="Known Problems for Controllers",
    )
    known_problems_for_panels = fields.Selection(
        [
            ("Cirrus Output Port Problem", "Cirrus Output Port Problem"),
            (
                "Light House Internal Connector Issue",
                "Light House Internal Connector Issue",
            ),
            ("Edge of Panel Diodes(s) Out", "Edge of Panel Diodes(s) Out"),
            ("LED Driver Failure", "LED Driver Failure"),
        ],
        string="Known Problems for Panels",
    )
    module_serial_number = fields.Char(string="Module Serial Number")
    nonconformity_affirmed = fields.Boolean(string="Nonconformity Affirmed")
    nonconformity_not_affirmed = fields.Boolean(string="Nonconformity Not Affirmed")
    panel_faults = fields.Selection(
        [
            ("Diode failure", "Diode failure"),
            ("Faulty input / output", "Faulty input / output"),
            ("Other", "Other"),
            ("Unresponsive face", "Unresponsive Face"),
        ],
        string="Panel Faults",
    )
    car_type = fields.Selection(
        [
            ("Panel(s)", "Panel(s)"),
            ("Component(s)", "Component(s)"),
            ("Controller(s)", "Controller(s)"),
        ],
        string="CAR Type",
    )
    review_pending = fields.Boolean(string="Review")
    root_cause_analysis = fields.Html(string="Root Cause Analysis")


class QualityDispositionOption(models.Model):
    _name = "quality.disposition.option"
    _description = "Quality Disposition Options"

    name = fields.Char(string="Name")
