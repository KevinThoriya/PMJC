from odoo import models, fields, api


class ResEmployee(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one('hr.employee', string="Employee")

    @api.model
    def create(self, val):
        res = super(ResEmployee, self).create(val)

        return res


class ResPartner(models.Model):
    _inherit = "res.partner"

    group_id = fields.Many2one('project.group', string="Default Project Group")

