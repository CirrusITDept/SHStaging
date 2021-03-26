# -*- coding: utf-8 -*-
import odoo
from odoo import api, fields, models, _


class ImLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'
    live_chat = fields.Boolean(string='Live Chat Channel', help="Select this for live chat account.")


class LiveChatLog(models.Model):
    _name = "live.chat.log"
    live_chat_log = fields.Text('Live Chat Log')
    livechat_channel_id = fields.Many2one('im_livechat.channel', 'Channel')

class Message(models.Model):
    _inherit = 'mail.message'
    livechat_author = fields.Char('Live Chat Author')

class MailChannel(models.Model):
    _inherit = 'mail.channel'
    live_chatid = fields.Char('Chat ID')