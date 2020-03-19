from odoo import models, fields, api


class Res(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one('hr.employee', string="Employee")

    @api.model
    def create(self, val):
        res = super(Res, self).create(val)
        emp = self.env['hr.employee'].create(
            {'name': res.name, 'work_email': res.login, 'user_id': res.id}
        )
        res.employee_id = emp.id
        return res
