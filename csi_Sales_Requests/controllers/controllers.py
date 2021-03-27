# -*- coding: utf-8 -*-
# from odoo import http


# class ItRequest(http.Controller):
#     @http.route('/it_request/it_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/it_request/it_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('it_request.listing', {
#             'root': '/it_request/it_request',
#             'objects': http.request.env['it_request.it_request'].search([]),
#         })

#     @http.route('/it_request/it_request/objects/<model("it_request.it_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('it_request.object', {
#             'object': obj
#         })
