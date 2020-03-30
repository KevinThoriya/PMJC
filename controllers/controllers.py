# -*- coding: utf-8 -*-
from odoo import http

# class Pmjc(http.Controller):
#     @http.route('/pmjc/pmjc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pmjc/pmjc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pmjc.listing', {
#             'root': '/pmjc/pmjc',
#             'objects': http.request.env['pmjc.pmjc'].search([]),
#         })

#     @http.route('/pmjc/pmjc/objects/<model("pmjc.pmjc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pmjc.object', {
#             'object': obj
#         })