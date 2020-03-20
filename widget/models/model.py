from odoo import fields, api, models


class Q2Pwidget(models.TransientModel):
    _inherit = 'project.project'
    _name = 'project.q2pwidget'

    @api.model
    def default_get(self, fields):
        res = {}
        active = self._context['active_id']
        # print(self.env['sale.order'].browse(self._context['active_id'])[0].partner_id.id) #['partner_id']
        res['partner_id'] = self.env['sale.order'].browse(self._context['active_id'])[0].partner_id.id
        return res

