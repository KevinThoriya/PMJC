from odoo import fields, api, models


class Q2Pwidget(models.TransientModel):
    _inherit = 'project.project'
    _name = 'project.q2pwidget'


    def create_project(self):
        pass