from odoo import models, fields, api


class Res(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one('hr.employee', string="Employee")

    @api.model
    def create(self, val):
        print("res.user are created...here", val['name'])
        res = super(Res, self).create(val)
        emp = self.env['hr.employee'].create(
            {'name': res.name, 'work_email': res.login, 'user_id': res.id}
        )
        res.employee_id = emp.id
        return res


class ResPartner(models.Model):
    _inherit = "res.partner"

    project_group = fields.Many2one('project.group', string="Default Project Group")

    def create(self, value):
        print("-----> res.partner has been created heree", value['name'])
        return super(ResPartner,self).create(value)
