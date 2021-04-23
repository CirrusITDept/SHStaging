# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class DisplayDisplay(models.Model):
    _name = "display.display"
    _inherit = "mail.thread"
    _description = "Display"

    account_manager_id = fields.Many2one('res.users', string="Account Manager", domain="['|', '|', ('name', 'ilike', 'ramsey'), ('name', 'ilike', 'moran'), ('name', '=', 'hilton')]", required=False)
    salesforce_id = fields.Char(string="Salesforce ID")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    number_of_power_injectors = fields.Char(string="Number of Power Injectors")
    additional_digital_details = fields.Text(string="Additional Digital Attributes")
    application = fields.Selection(
        [("New", "New"), ("Retrofit", "Retrofit")], string="Application",
    )
    breaker_rating = fields.Integer(string="Breaker Rating")
    cellular_enabled = fields.Boolean(string="Cellular Enabled")
    cellular_enabled_until = fields.Date(string="Cellular Enabled Until")
    cellular_paid = fields.Boolean(string="Cellular Paid")
    controller_mounting_location = fields.Selection(
        [
            ("Bottom of sign", "Bottom of sign"),
            ("Top of sign", "Top of sign"),
            ("Side of sign", "Side of sign"),
            ("Inside of sign", "Inside of sign"),
            ("Other", "Other"),
        ],
        string="Controller Mounting Location",
    )
    details = fields.Html(string="Details")
    display_as_a_service = fields.Many2one(
        "display.daas", string="Display as a Service"
    )
    # TODO display_id = fields.Char(string="Display ID")
    name = fields.Char(string="Display Name", track_visibility="always")
    display_setup = fields.Many2one("display.setup", string="Display Setup")
    distance_from_building = fields.Integer(string="Distance from Building (feet)")
    distributor = fields.Many2one(
        "res.partner", string="Distributor", track_visibility="always"
    )
    download_speed = fields.Integer(string="Download Speed (Mbps)")
    electrical_details = fields.Html(string="Electrical details")
    account = fields.Many2one(
        "res.partner", string="End User Account", track_visibility="always"
    )
    end_user_contact = fields.Many2one("res.partner", string="End User Contact")
    end_user_responsible_for_electrical = fields.Selection(
        [
            (
                "I am responsible for the electrical setup",
                "I am responsible for the electrical setup",
            ),
            (
                "The end user is responsible for the electrical setup",
                "The end user is responsible for the electrical setup",
            ),
            (
                "The sign shop is responsible for the electrical setup",
                "The sign shop is responsible for the electrical setup",
            ),
        ],
        string="End user responsible for electric",
    )
    end_user_responsible_for_internet = fields.Selection(
        [
            (
                "I am responsible for the internet setup",
                "I am responsible for the internet setup",
            ),
            (
                "The sign shop is responsible for the internet setup",
                "The sign shop is responsible for the internet setup",
            ),
        ],
        string="End user responsible for internet",
    )
    hardware = fields.Html(string="Hardware")
    hardware_type = fields.Selection(
        [("Cirrus", "Cirrus"), ("LH", "LH"), ("Grant", "Grant")], string="Hardware",
    )
    height = fields.Integer(string="Height (feet)", track_visibility="always")
    height_from_ground = fields.Integer(
        string="Height from Ground (feet)",
        help="How far off the ground is the bottom of the display?",
    )
    install_date = fields.Date(string="Install Date", track_visibility="always")
    internet_connection_type = fields.Selection(
        [
            ("Hardwired", "Hardwired"),
            ("Wireless AP", "Wireless AP"),
            ("Wireless AP/Bridge", "Wireless AP/Bridge"),
            ("Mobile hotspot", "Mobile hotspot"),
            ("Cellular Broadband", "Cellular Broadband"),
        ],
        string="Internet Connection Type",
    )
    internet_speed_class = fields.Selection(
        [
            ("Dial-up", "Dial-up"),
            ("DSL", "DSL"),
            ("Broadband", "Broadband"),
            ("Cellular Broadband", "Cellular Broadband"),
            ("Fiber", "Fiber"),
            ("Mobile data", "Mobile data"),
        ],
        string="Internet Speed Class",
    )
    it_contact_email = fields.Char(string="IT Contact Email")
    it_contact_name = fields.Char(string="IT Contact Name")
    it_contact_phone = fields.Char(string="IT Contact Phone")
    labor_warranty = fields.Selection(
        [
            ("1 year", "1 year"),
            ("2 years", "2 years"),
            ("3 years", "3 years"),
            ("4 years", "4 years"),
            ("5 years", "5 years"),
            ("None", "None"),
        ],
        string="Labor Warranty",
    )
    screenhub_version = fields.Selection(
        [
            ("Cypher", "Cypher"),
            ("Cirrus LED Cloud Player", "Cirrus LED Cloud Player"),
            ("ScreenHub v1.0", "ScreenHub v1.0"),
            ("ScreenHub v2.0", "ScreenHub v2.0"),
        ],
        string="Media Player Version",
    )
    model = fields.Selection(
        [
            ("N2", "N2"),
            ("Blade", "Blade"),
            ("Blade N", "Blade N"),
            ("Solo", "Solo"),
            ("Blade-M-Nucleus", "Blade-M-Nucleus"),
            ("Blade C", "Blade C"),
            ("Blade X", "Blade X"),
            ("Blade-M-Link88", "Blade-M-Link88"),
        ],
        string="Model",
    )
    mounting_type = fields.Selection(
        [
            ("Single Pole", "Single Pole"),
            ("Double Pole", "Double Pole"),
            ("Monument", "Monument"),
            ("Side of Building", "Side of Building"),
            ("Pylon", "Pylon"),
            ("Other", "Other"),
        ],
        string="Mounting Type",
    )
    network_settings_restrictions = fields.Html(string="Network Settings/Restrictions")
    new_electrical_line = fields.Selection(
        [("Yes", "Yes"), ("No", "No")], string="New Electrical Line",
    )
    number_of_faces = fields.Selection(
        [
            ("One (1)", "One (1)"),
            ("Two (2)", "Two (2)"),
            ("Three (3)", "Three (3)"),
            ("Four (4)", "Four (4)"),
        ],
        string="Number of faces",
        track_visibility="always",
    )
    won_sale_id = fields.Many2one("sale.order", string="Sales")
    helpdesk_id = fields.Many2one("helpdesk.ticket", string="Helpdesk Ticket", copy=False)
    opportunity = fields.Many2one("crm.lead", string="Opportunity")
    own_dedicated_circuit = fields.Selection(
        [("Yes", "Yes"), ("No", "No")], string="Own Dedicated Circuit",
    )
    owner_id = fields.Many2one("crm.lead", string="Owner")
    panel_control_software = fields.Selection(
        [
            ("LED Configuration Guru", "LED Configuration Guru"),
            ("Octopus", "Octopus"),
            ("Link88", "Link88"),
            ("BLADE System Player", "BLADE System Player"),
            ("Nucleus", "Nucleus"),
        ],
        string="Panel Control Software",
    )
    firmware_version = fields.Selection(
        [
            ("Grant", "Grant"),
            ("Version 6", "Version 6"),
            ("Version 7", "Version 7"),
            ("Version 7.0_SOLO", "Version 7.0_SOLO"),
            ("Version 8", "Version 8"),
            ("Version 9", "Version 9"),
            ("Version 9.3", "Version 9.3"),
            ("Version 9.4", "Version 9.4"),
            ("Version 9.5", "Version 9.5"),
            ("Version 9.X_SOLO", "Version 9.X_SOLO"),
            ("Version 9.7_CHIP1", "Version 9.7_CHIP1"),
            ("Version 9.5.1", "Version 9.5.1"),
            ("Version 9.8", "Version 9.8"),
            ("Version 9.9", "Version 9.9"),
        ],
        string="Panel Firmware Version",
    )
    physical_notes = fields.Html(string="Physical Notes")
    pitch = fields.Selection(
        [
            ("4mm", "4mm"),
            ("6mm", "6mm"),
            ("9mm", "9mm"),
            ("12mm", "12mm"),
            ("15mm", "15mm"),
            ("16mm", "16mm"),
            ("19mm", "19mm"),
        ],
        string="Pitch",
    )
    display_matrix = fields.Char(string="Display Matrix", store=True, copy=False)
    projected_install_date = fields.Date(string="Projected Install Date")
    purchase_date = fields.Date(string="Purchase Date")
    screenhub_2_0_display_id = fields.Char(string="ScreenHub 2.0 Display ID")
    screenhub_display_id = fields.Char(string="Screenhub Display ID")
    sign_shop = fields.Many2one(
        "res.partner", string="Sign Shop", track_visibility="always"
    )
    sign_shop_contact = fields.Many2one("res.partner", string="Sign Shop Contact")
    sign_shop_responsible_for_electric = fields.Selection(
        [
            (
                "I am responsible for the electrical setup",
                "I am responsible for the electrical setup",
            ),
            (
                "The end user is responsible for the electrical setup",
                "The end user is responsible for the electrical setup",
            ),
        ],
        string="Sign shop responsible for electric",
    )
    sign_shop_responsible_for_internet = fields.Selection(
        [
            (
                "I am responsible for the internet setup",
                "I am responsible for the internet setup",
            ),
            (
                "The end user is responsible for the internet setup",
                "The end user is responsible for the internet setup",
            ),
        ],
        string="Sign shop responsible for internet",
    )
    software_version = fields.Char(string="Software Version")
    status = fields.Selection(
        [
            ("Purchased", "Purchased"),
            ("Tested", "Tested"),
            ("Shipped", "Shipped"),
            ("Received", "Received"),
            ("Received - Setup in shop", "Received - Setup in shop"),
        ],
        string="Status",
        default="Purchased",
        track_visibility="always",
    )
    status_old = fields.Char(string="Salesforce Status")
    upload_speed = fields.Integer(string="Upload Speed (Mbps)")
    electical_setup_voltage = fields.Selection(
        [
            ("110 V", "110 V"),
            ("120 V", "120 V"),
            ("208 V", "208 V"),
            ("220 V", "220 V"),
            ("240 V", "240 V"),
        ],
        string="Voltage",
    )
    width = fields.Integer(string="Width (feet)", track_visibility="always")
    opportunity_count = fields.Integer(
        compute="_compute_record_count", string="Opportunity Count"
    )
    sale_order_count = fields.Integer(
        compute="_compute_record_count", string="Sale Order Count"
    )
    quality_alert_count = fields.Integer(
        compute="_compute_record_count", string="Quality Alert Count"
    )
    helpdesk_ticket_count = fields.Integer(
        compute="_compute_record_count", string="Helpdesk Ticket Count"
    )
    manufacturing_order_count = fields.Integer(
        compute="_compute_record_count", string="Manufacturing Order Count"
    )
    salesforce_order_count = fields.Integer(
        string="Order Count", compute="_compute_record_count"
    )
    request_ids = fields.One2many("sign.request", "display_id", string="Sign Requests")
    request_count = fields.Integer(
        string="Request Count", compute="_compute_record_count"
    )

    def create_install_ticket(self):
        view_id = self.env.ref("helpdesk.helpdesk_ticket_view_form").id
        team_id = False
        helpdesk_team_id = self.env["helpdesk.team"].search([("id", "=", 12)], limit=1)
        if helpdesk_team_id and helpdesk_team_id.name == "Preinstall":
            team_id = helpdesk_team_id.id
        else:
            team = self.env["helpdesk.team"].search(
                [("name", "=", "Preinstall")], limit=1
            )
            if team:
                team_id = team.id
        return {
            'name': _('Create Install Ticket'),
            'type': 'ir.actions.act_window',
            'view_id': view_id,
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'context': {
                'default_display_id': self.id,
                'default_name': f"{self.name} - {'PreInstall'}",
                'default_projected_install_date': self.projected_install_date,
                'default_partner_id': self.end_user_contact.id if self.end_user_contact else False,
                'default_partner_name': self.end_user_contact.name if self.end_user_contact else False,
                'default_partner_email': self.end_user_contact.email if self.end_user_contact else False,
                'default_partner_phone': self.end_user_contact.phone if self.end_user_contact else False,
                'default_partner_sign_id': self.sign_shop.id if self.sign_shop else False,
                'default_partner_end_id': self.account.id if self.account else False,
                'default_team_id': team_id if team_id else False,
                'default_user_id': self.account_manager_id.id if self.account_manager_id else False,
            }
        }

    @api.constrains("won_sale_id")
    def set_display_id(self):
        sale = self.env["sale.order"].search([("id", "=", self.won_sale_id.id)])
        sale.update({"display_id": self.id})

    def open_sign_request(self):
        self.ensure_one()
        action = self.env.ref("sign.sign_request_action").read()[0]
        action["context"] = {"display_id": self.id}
        action["domain"] = [("id", "in", self.request_ids.ids)]
        action["views"] = [(False, "kanban"), (False, "form")]
        return action

    def open_salesforce_order(self):
        self.ensure_one()
        action = self.env.ref("base_csi.action_window_salesforce_order").read()[0]
        action["context"] = {
            "default_display": self.id,
        }
        orders = self.env["salesforce.order"].search([("display", "=", self.id)])
        action["domain"] = [("id", "in", orders.ids)]
        action["views"] = [(False, "tree"), (False, "form")]
        if len(orders) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = orders.id
        return action

    def _compute_record_count(self):
        for display in self:
            opp = self.env["crm.lead"].search(
                [("display_id", "=", display.id), ("type", "=", "opportunity")]
            )
            opp |= display.opportunity
            display.opportunity_count = len(opp)
            display.sale_order_count = self.env["sale.order"].search_count(
                [("display_id", "=", display.id)]
            )
            display.quality_alert_count = self.env["quality.alert"].search_count(
                [("display_id", "=", display.id)]
            )
            display.helpdesk_ticket_count = self.env["helpdesk.ticket"].search_count(
                [("display_id", "=", display.id), ("stage_id.is_close", "=", False)]
            )
            display.manufacturing_order_count = self.env["mrp.production"].search_count(
                [("display_id", "=", display.id)]
            )
            display.salesforce_order_count = self.env["salesforce.order"].search_count(
                [("display", "=", display.id)]
            )
            display.request_count = len(display.request_ids)


class DisplayDaas(models.Model):
    _name = "display.daas"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Display as a Service"

    salesforce_id = fields.Char(string="Salesforce ID")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    account_contact = fields.Many2one("res.partner", string="Account Contact")
    account_name_del = fields.Many2one("res.partner", string="Account Name")
    account_number = fields.Char(string="Account Number")
    addtional_screen_quantity = fields.Integer(string="Addtional Screen Quantity")
    bank_account_name = fields.Char(string="Bank Account Name")
    billing_contact_email = fields.Char(string="Billing Contact Email")
    billing_contact_name = fields.Char(string="Billing Contact Name")
    billing_contact_phone = fields.Char(string="Billing Contact Phone")
    billing_contact_title = fields.Char(string="Billing Contact Title")
    business_checking = fields.Boolean(string="Business Checking")
    business_saving = fields.Boolean(string="Business Saving")
    client_city = fields.Char(string="Client City")
    client_country = fields.Char(string="Client Country")
    client_name = fields.Char(string="Client Name")
    client_state = fields.Char(string="Client State")
    client_street = fields.Char(string="Client Street")
    client_zip = fields.Char(string="Client Zip")
    contract_number = fields.Integer(string="Contract Number")
    daas_package_quantity = fields.Integer(string="DaaS Package Quantity")
    name = fields.Char(string="Display as a Service Name")
    double_sided = fields.Boolean(string="Double Sided")
    effective_date = fields.Date(string="Effective Date")
    height_feet = fields.Integer(string="Height (feet)")
    owner = fields.Many2one("res.users", string="Owner")
    personal_checking = fields.Boolean(string="Personal Checking")
    personal_saving = fields.Boolean(string="Personal Saving")
    principal_contact_email = fields.Char(string="Principal Contact Email")
    principal_contact_name = fields.Char(string="Principal Contact Name")
    principal_contact_phone = fields.Char(string="Principal Contact Phone")
    principal_contact_title = fields.Char(string="Principal Contact Title")
    routing_number = fields.Char(string="Routing Number")
    side_information = fields.Char(string="Side Information")
    sqft = fields.Char(string="SqFt")
    sqft_calculation = fields.Integer(string="SqFt Calculation")
    total_cost = fields.Float(string="Total Cost")
    width_feet = fields.Integer(string="Width (feet)")


class DisplaySetup(models.Model):
    _name = "display.setup"
    _description = "Display Setup"

    salesforce_id = fields.Char(string="Salesforce ID")
    salesforce_create_date = fields.Datetime(string="Salesforce Create Date")
    account_email = fields.Char(string="Account Email")
    any_ideas_for_content = fields.Text(string="Any ideas for content?")
    can_they_do_video = fields.Selection(
        [("Yes", "Yes"), ("No", "No")], string="Can they do video?",
    )
    cirrus_system_model = fields.Selection(
        [
            ("Blade 12mm", "Blade 12mm"),
            ("Blade 16mm", "Blade 16mm"),
            ("Blade 19mm", "Blade 19mm"),
            ("Solo ICE", "Solo ICE"),
            ("Solo FIRE", "Solo FIRE"),
            ("N2 19mm", "N2 19mm"),
            ("N2 12mm", "N2 12mm"),
        ],
        string="Cirrus System Model",
    )
    city = fields.Char(string="City")
    cloud_completed_date = fields.Date(string="Cloud account completed date")
    cloud_account_created = fields.Boolean(string="Cloud Account Created")
    cloud_account_linked_to_controller = fields.Boolean(
        string="Cloud Account linked to controller"
    )
    cloud_training_completed = fields.Date(string="Cloud Training Completed")
    cloud_walk_scheduled_for = fields.Datetime(string="Cloud walk scheduled for")
    contact_email = fields.Char(string="Contact Email")
    contact_name = fields.Text(string="Contact Name")
    contact_phone_number = fields.Char(string="Contact Phone Number")
    controller_id = fields.Char(string="Controller ID")
    country = fields.Char(string="Country")
    direct_line_of_site_from_antenna_to_sign = fields.Selection(
        [("Yes", "Yes"), ("No", "No")],
        string="Direct line of site from antenna to sign",
        help="Wifi Transmitter: Obstructions may cause a connectivity issue \
            and an unreliable internet connection. Cirrus cannot be \
            responsible for site conditions that affect internet \
            connectivity.",
    )
    X00019226 = fields.Selection(
        [("Yes", "Yes"), ("No", "No")],
        string="Discussed Installation Documentation?",
        help="Does Sign Shop has all relevant documentation? Install manual, \
            WiFi installation manual Discuss with the sign shop what each \
            document is for and its content and make sure they don't have any \
            questions.",
    )
    display_address = fields.Html(
        string="Display Address",
        help="Install address, please, if possible, include a google map link.",
    )
    display_height = fields.Integer(string="Display Height")
    display_id = fields.Char(string="Display ID")
    display_info_stage = fields.Selection(
        [
            ("To schedule call", "To schedule call"),
            ("Call set up", "Call set up"),
            (
                "Initial call --- Waiting for more information",
                "Initial call --- Waiting for more information",
            ),
            ("Stage completed", "Stage completed"),
        ],
        string="Display Info Stage",
    )
    name = fields.Char(string="Display Name")
    display_notes = fields.Html(string="Display Notes")
    display_width = fields.Integer(string="Display Width")
    end_user_email = fields.Char(string="End User Email")
    cloud_account_created = fields.Boolean(string="Cloud Account Created")
    eu_completed = fields.Boolean(string="End User Info Completed")
    end_user_name = fields.Char(string="End User name")
    end_user_phone = fields.Char(string="End User Phone")
    end_s_user_info = fields.Selection(
        [
            ("To schedule call", "To schedule call"),
            ("Call set up", "Call set up"),
            (
                "Initial call --- Waiting for more information",
                "Initial call --- Waiting for more information",
            ),
            ("Stage completed", "Stage completed"),
        ],
        string="End's User Info Stage",
    )
    estimated_install_date = fields.Date(string="Estimated install date")
    free_content_status = fields.Selection(
        [
            ("Waiting on free content", "Waiting on free content"),
            ("Free content delivered", "Free content delivered"),
        ],
        string="Free Content Status",
    )
    got_it_contact_info = fields.Selection(
        [("No", "No"), ("Yes", "Yes")], string="Got IT Contact info?",
    )
    has_a_survey_site_been_completed = fields.Selection(
        [("No", "No"), ("Yes", "Yes")],
        string="Has a survey site been completed?",
        help="Determine the closest active internet port to sign: Wall jack\
            , network switch, etc.",
    )
    how_will_it_be_mounted = fields.Html(string="How will it be mounted?")
    install_checklist_stage = fields.Selection(
        [
            ("To schedule call", "To schedule call"),
            ("Call set up", "Call set up"),
            (
                "Initial call --- Waiting for more information",
                "Initial call --- Waiting for more information",
            ),
            ("Stage completed", "Stage completed"),
        ],
        string="Install checklist stage",
    )
    install_completed = fields.Boolean(string="Install Completed")
    installed_date = fields.Date(string="Install date")
    completed_date = fields.Datetime(
        string="Installation checklist call time",
        help="Which date and time were the checklist was discussed with the sign shop",
    )
    installerinfo = fields.Boolean(string="Installer information completed")
    installer_information_completed_date = fields.Date(
        string="Installer information completed date"
    )
    notes = fields.Html(string="Installer Notes")
    internet_call_time = fields.Datetime(string="Internet Call time")
    internet = fields.Selection(
        [
            ("Wifi Transmitter", "Wifi Transmitter"),
            ("Broadband/hotspot", "Broadband/hotspot"),
            ("Ethernet direct", "Ethernet direct"),
            ("Other", "Other"),
        ],
        string="Internet Connection",
    )
    internet_connection_info_completed = fields.Boolean(
        string="Internet Connection Info completed"
    )
    internet_connection_info_completed_date = fields.Date(
        string="Internet Connection Info completed date"
    )
    internet_connection_notes = fields.Html(string="Internet connection notes")
    internet_connection_stage = fields.Selection(
        [
            ("To schedule call", "To schedule call"),
            ("Call set up", "Call set up"),
            (
                "Initial call --- Waiting for more information",
                "Initial call --- Waiting for more information",
            ),
            ("Stage completed", "Stage completed"),
        ],
        string="Internet Connection Stage",
    )
    it_contact_email = fields.Char(string="It contact email")
    it_contact_name = fields.Char(string="It Contact Name")
    it_contact_phone = fields.Char(string="IT contact Phone")
    it_support_call = fields.Datetime(string="It Support Call Date")
    it_support_completed = fields.Boolean(string="IT support completed")
    it_support_completed_date = fields.Date(string="IT support completed date")
    it_support = fields.Selection(
        [
            ("To schedule call", "To schedule call"),
            ("Call set up", "Call set up"),
            (
                "Initial call --- Waiting for more information",
                "Initial call --- Waiting for more information",
            ),
            ("Stage completed", "Stage completed"),
        ],
        string="It Support Stage",
    )
    length_of_ethernet_cable = fields.Char(
        string="Length of Ethernet Cable?",
        help="The Ethernet cable between the wireless antenna and the power \
            over ethernet (PoE) must be less than 50ft. The Ethernet cable \
            between the PoE and the router/modem/wall jack can be any length.",
    )
    loaded_to_the_install_map = fields.Boolean(string="Loaded to the install map")
    n2_has_an_outlet_been_installed = fields.Selection(
        [("Yes", "Yes"), ("No", "No")],
        string="N2: Has an outlet been installed?",
        help="If an N2 display has been purchased, has an outlet been \
            installed at the sign to plug in the second WiFi unit?",
    )
    network_restrictions = fields.Text(
        string="Network restrictions?",
        help="Are there any network restrictions(bandwidth limitations, \
            firewalls, content filters, etc.) that could affect connectivity?)",
    )
    new_retrofit = fields.Selection(
        [("New", "New"), ("Retrofit", "Retrofit")],
        string="New/ Retrofit",
        help="New sign or retrofit?",
    )
    opportunity = fields.Many2one("crm.lead", string="Opportunity")
    opportunity_description = fields.Text(string="Opportunity Description")
    sales_notes = fields.Text(string="Opportunity Description and end users")
    opportunity_end_user_notes = fields.Text(string="Opportunity End user notes")
    order = fields.Many2one("sale.order", string="Order")
    salesforce_order = fields.Many2one("salesforce.order", string="Salesforce Order")
    order_type = fields.Selection(
        [
            ("Direct", "Direct"),
            ("Distributor- GSG", "Distributor - GSG"),
            ("Distributor - Martin Supplies", "Distributor - Martin Supplies"),
            ("Distributor - EM Plastic", "Distributor - EM Plastic"),
        ],
        string="Order Type",
    )
    other_email = fields.Char(string="Other email")
    password = fields.Char(string="Password")
    pixel_matrix = fields.Char(string="Pixel Matrix")
    completed = fields.Boolean(string="Project Completed")
    project_owner = fields.Many2one("res.users", string="Project Owner")
    project_owner_email = fields.Char(string="Project Owner email")
    purchase_order = fields.Char(string="Purchase Order")
    reconfirmed = fields.Boolean(
        string="Reconfirmed installed date?",
        help="Follow up with sign shop to re-confirm install date five days \
            prior to install. Reinfornces that sign shop must call Tech \
            Support while on site installing the display.",
    )
    responsible_for_internet_connectivity = fields.Selection(
        [("End User", "End User"), ("Sign Shop", "Sign Shop")],
        string="Responsible for internet connectivity?",
        help="Who is responsible to make sure that the display is connected \
            to the internet (connecting the display to the end user's \
            network)?",
    )
    it_contact_if_they_are_responsible = fields.Text(
        string="Responsible for internet to the sign?",
        help="Who is the person responsible for connecting the sign to \
            the internet. That person should go be aware of all security \
            issues and network restrictions and should be on site when \
            install happens.",
    )
    responsible_for_led_cloud_account = fields.Selection(
        [("End User", "End User"), ("Sign Shop", "Sign Shop")],
        string="Responsible for LED Cloud Account?",
        help="Who will be managing the content(end user or sign shop)? This will \
            determine if the sign can be connected to the sign shop's LED \
            Cloud account",
    )
    sign_shop_name = fields.Char(string="Sign Shop Name")
    sign_shop_needs_an_led_cloud_training = fields.Selection(
        [
            ("No", "No"),
            ("Yes- To be scheduled", "Yes- To be scheduled"),
            ("Yes- Scheduled", "Yes- Scheduled"),
            ("Yes- Completed", "Yes- Completed"),
        ],
        string="Sign shop needs an LED cloud training?",
    )
    single_double_sided = fields.Selection(
        [("Single Sided", "Single Sided"), ("Double Sided", "Double Sided")],
        string="Single/ Double Sided",
    )
    stage_on_all = fields.Char(string="Stage on all sections",)
    state = fields.Char(string="State")
    test_in_shop = fields.Selection(
        [("No", "No"), ("Yes", "Yes")],
        string="Test in Shop?",
        help="Are you planning on setting up the display in your shop \
            prior to the install?",
    )
    they_have_ethernet_cables = fields.Selection(
        [("Yes", "Yes"), ("No", "No")],
        string="They have Ethernet cables?",
        help="Cirrus does not provide ethernet cables",
    )
    to_run_new_electric = fields.Selection(
        [("No", "No"), ("Yes", "Yes")],
        string="To run new electric?",
        help="Does the project require a new electrical line to be run \
            to the display?",
    )
    tracking_nu = fields.Char(string="Tracking number")
    username = fields.Char(string="Username")
    website = fields.Char(string="Website")
    zip_c = fields.Char(string="ZIP")
