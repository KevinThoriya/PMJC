# -*- coding: utf-8 -*-
from odoo import http

# class Aproject(http.Controller):
#     @http.route('/aproject/aproject/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aproject/aproject/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aproject.listing', {
#             'root': '/aproject/aproject',
#             'objects': http.request.env['aproject.aproject'].search([]),
#         })

#     @http.route('/aproject/aproject/objects/<model("aproject.aproject"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aproject.object', {
#             'object': obj
#         })