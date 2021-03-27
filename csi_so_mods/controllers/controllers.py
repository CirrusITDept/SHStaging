# -*- coding: utf-8 -*-
# from odoo import http


# class CsiSoMods(http.Controller):
#     @http.route('/csi_so_mods/csi_so_mods/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/csi_so_mods/csi_so_mods/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('csi_so_mods.listing', {
#             'root': '/csi_so_mods/csi_so_mods',
#             'objects': http.request.env['csi_so_mods.csi_so_mods'].search([]),
#         })

#     @http.route('/csi_so_mods/csi_so_mods/objects/<model("csi_so_mods.csi_so_mods"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('csi_so_mods.object', {
#             'object': obj
#         })
