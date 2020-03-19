from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    project_ids = fields.Many2many('project.project', 'rel_project_employee', 'emp_id', 'project_id', string="Project")

