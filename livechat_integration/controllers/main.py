from odoo import fields, http, tools, _
from odoo.http import request
import json
import werkzeug.wrappers
import logging


class MyController(http.Controller):

    @http.route('/chat/rate', type='json', auth="public", methods=['GET', 'POST'], csrf=False)
    def save_rate(self, **kwargs):
        params = request.httprequest.get_data()
        params = json.loads(params)
        if 'payload' in params and 'thread_id' in params['payload'] and 'properties' in params[
            'payload'] and 'rating' in params['payload']['properties'] and 'score' in params['payload']['properties'][
            'rating']:
            score = params['payload']['properties']['rating']['score']
            if score == 1:
                score = 10
                rating_text = 'satisfied'
            else:
                score = 0
                rating_text = 'not_satisfied'
            thread_id = params['payload']['thread_id']
            mail_channel = request.env['mail.channel'].sudo().search([('live_chatid', '=', thread_id)], limit=1)
            res_model_id = request.env['ir.model'].sudo().search([('model', '=', 'mail.channel')], limit=1)
            parent_res_model_id = request.env['ir.model'].sudo().search([('model', '=', 'im_livechat.channel')],
                                                                        limit=1)
            request.env['rating.rating'].sudo().create({
                'res_model_id': res_model_id.id,
                'parent_res_model_id': parent_res_model_id.id,
                'res_id': mail_channel.id,
                'parent_res_id': mail_channel.livechat_channel_id.id,
                'rating': score,
                'rating_text': rating_text,
            })
        return werkzeug.wrappers.Response(
            status=200,
            response=json.dumps(
                {'success': True}
            ),
        )

    @http.route('/livechat/create', type='json', auth="public", methods=['GET', 'POST'], csrf=False)
    def save_kwargs(self, **kwargs):
        params = request.httprequest.get_data()
        params = json.loads(params)
        livechat_channel = request.env['im_livechat.channel'].sudo().search([('live_chat', '=', True)], limit=1)
        if livechat_channel:
            request.env['live.chat.log'].sudo().create(
                {'live_chat_log': params, 'livechat_channel_id': livechat_channel.id})
            request.env.cr.commit()
            if 'chat' in params and 'messages' in params['chat']:
                users_email = []
                authors = []
                chat_messages = []
                chat_id = params['chat']['id']
                for message in params['chat']['messages']:
                    authors.append(message['author_name'])
                    if message['user_type'] == 'agent':
                        if 'bot' in message['author_name'].lower():
                            author_name = message['author_name']
                        else:
                            author_name = message['author_name'] + '(Agent)'

                        users_email.append(message['agent_id'])
                        author = request.env['res.users'].sudo().search(
                            [('login', '=', message['agent_id'])]).partner_id.id
                    else:
                        author = ''
                        author_name = message['author_name'] + '(Visitor)'
                    chat_messages_dict = {'message_type': 'comment',
                                          'body': message['text'],
                                          'moderation_status': 'accepted',
                                          'author_id': author,
                                          'livechat_author': author_name,
                                          'model': 'mail.channel',
                                          }
                    chat_messages.append((0, 0, chat_messages_dict))
                users_email = list(set(users_email))
                authors = list(set(authors))
                users = request.env['res.users'].sudo().search([('login', 'in', users_email)])
                attendees = ','.join(map(str, authors))
                for user in users.ids:
                    livechat_channel.write({'user_ids': [(4, user)]})
                request.env['mail.channel'].sudo().create({
                    'livechat_channel_id': livechat_channel.id,
                    'name': attendees,
                    'live_chatid': chat_id,
                    'message_ids': chat_messages,
                    'channel_message_ids': chat_messages,
                })

        return werkzeug.wrappers.Response(
            status=200,
            response=json.dumps(
                {'success': True}
            ),
        )
