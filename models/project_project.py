from odoo import models, fields, api


class Project(models.Model):
    _inherit = "project.project"

    group_id = fields.Many2one('project.groups', string="Project Group")
    start_date = fields.Date()
    expected_end_date = fields.Date()
    expiration_date = fields.Date()
    priority = fields.Selection([('0', 'Null'), ('1', 'Low'), ('2', 'Medium'), ('3', 'High')])
    milestone_ids = fields.One2many('project.milestone', 'project_id', string='Milestones')
    employee_ids = fields.Many2many("hr.employee", 'rel_project_employee', 'project_id', 'emp_id', string="Employees")
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount = fields.Monetary(currency_field='currency_id')
    unit_measure = fields.Selection([('byWeek', 'by week'), ('byMonth', 'by month'), ('byHour', 'by Hour')])
    billing_rate = fields.Float(string="Billing Rate")
    actual_rate = fields.Float(string="actual Rate")
    cost_rate_ids = fields.One2many('project.cost.rate', 'project_id', string="Cost Rate")
    approved_rate_ids = fields.One2many('project.approved.rate', 'project_id', string="Approved Rate")
    unit_of_measure = fields.Selection(string="Default Unit of Measure", selection=[('week', 'By Week'), ('hour', 'By Hour'), ('month', 'By Month')])
    timesheet_grouping = fields.Selection(string="Default Timesheet Grouping", selection=[('week', 'By Week'), ('hour', 'By Hour'), ('month', 'By Month')])

    @api.model
    def create(self, val):
        res = super(Project, self).create(val)
        self.env['project.approved.rate'].create({'unit_of_measure':  'hour', 'rate': res.billing_rate, 'project_id': res.id})
        return res


class ProjectGroup(models.Model):
    _name = "project.groups"

    name = fields.Char(string="Name of Group")
    active = fields.Boolean(string="active", default=True)


class CostRate(models.Model):
    _name = "project.cost.rate"
    _description = 'CostRate'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    cost_rate = fields.Integer(string="Cost Rate")
    is_billable = fields.Boolean(string="is_billable?")
    billing_percent = fields.Integer(string='Billing %', required=False)
    project_id = fields.Many2one('project.project', string="Project")


class ApprovedRate(models.Model):
    _name = "project.approved.rate"
    _description = 'ApprovedRate'

    unit_of_measure = fields.Selection(string="Unit of Measure", selection=[('week', 'By Week'), ('hour', 'By Hour'), ('month', 'By Month')])
    rate = fields.Float(string="Rate")
    project_id = fields.Many2one('project.project', string="project")

