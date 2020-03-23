from odoo import models, fields, api
import datetime


class ProjectAreapath(models.Model):
    _name = "project.areapath"

    name = fields.Char()
    active = fields.Boolean(default=True)
    project_id = fields.Many2one('project.project')


class ProjectIteration(models.Model):
    _name = "project.iteration"

    name = fields.Char()
    azure_id = fields.Char()
    active = fields.Boolean(default=True)
    startdate = fields.Date(default=fields.Date.context_today)
    enddate = fields.Date()
    project_id = fields.Many2one('project.project', string="project")


class ProjectTaskUpdate(models.Model):
    _name = "project.task.update"

    changed_date = fields.Date(index=True)
    changed_by_id = fields.Many2one('res.users', string='Changed By')
    remaining_work_hour = fields.Float()
    original_estimate_hour = fields.Float()
    complete_work_hour = fields.Float()
    task_id = fields.Many2one("project.task", string="Task")


class ProjectTask(models.Model):
    _inherit = "project.task"

    azure_id = fields.Char(string="Azure Id", index=True)
    areapath_id = fields.Many2one('project.areapath', string="AreaPath")
    iteration_path = fields.Char()
    iteration_id = fields.Many2one('project.iteration', string="Iteration")
    week = fields.Char(compute="_compute_week", store=True, string="Week")
    emp_id = fields.Many2one('hr.employee', string="Employee", related='user_id.employee_id', store=True)
    user_id = fields.Many2one('res.users', string='Assigned to', index=True, track_visibility=False, default=False,
                              related=False, store=True)
    reason = fields.Char()
    created_date = fields.Date(index=True)
    created_by_id = fields.Many2one('res.users', string='Created By')
    priority = fields.Selection([(4, 4), (3, 3), (2, 2), (1, 1), ], default='1', string="Priority")
    title = fields.Char()
    description = fields.Html()
    parent_task_id = fields.Many2one('project.task', string='Parent', default=None)
    child_ids = fields.One2many('project.task', 'parent_task_id', string='Tasks', domain=[('active', '=', True)])
    type = fields.Selection(selection=[('Bug', 'Bug'), ('Code Review Request', 'Code Review Request'),
                                       ('Code Review Response', 'Code Review Response'),
                                       ('Epic', 'Epic'), ('Feature', 'Feature'),
                                       ('Feedback Request', 'Feedback Request'),
                                       ('Feedback Response', 'Feedback Response'), ('Shared Steps', 'Shared Steps'),
                                       ('Test Case', 'Test Case'),
                                       ('Test Plan', 'Test Plan'), ('Test Suite', 'Test Suite'),
                                       ('User Story', 'User Story'), ('Issue', 'Issue'),
                                       ('Shared Parameter', 'Shared Parameter'), ('Task', 'Task'),
                                       ('Change Request', 'Change Request')])
    project_id = fields.Many2one('project.project', string="Project", index=True, track_visibility='onchange',
                                 default=lambda self: self.env.context.get('default_project_id'))
    stage_id = fields.Many2one('project.task.type', string='Stage', index=True, domain="[]",
                               track_visibility='onchange')
    task_update_ids = fields.One2many('project.task.update', 'task_id', string='Task Update', ondelete='cascade')
    planned_hours = fields.Float(compute='_compute_get_hours', store=False, string='Original Estimate Hours')
    remaining_hours = fields.Float(compute='_compute_get_hours', store=False, string='Remaining Hours')
    effective_hours = fields.Float(compute='_compute_get_hours', store=False, string='Hours Spent')
    progress = fields.Float(compute='_compute_get_hours', store=False, string='Progress', group_operator="avg")
    total_hours_spent = fields.Float(compute='_compute_get_hours', store=False, string='Total Hours',
                                     help="Total Time on This Task. = remaining + compeleted")

    @api.depends('created_date')
    def _compute_week(each):
        for self in each:
            if self.created_date:
                created_date = datetime.datetime.strptime(self.created_date, "%Y-%m-%d")
                cal = created_date.isocalendar()
                value = f"{cal[1]}/{cal[0]}"
                self.week = value

    @api.depends('task_update_ids', 'child_ids')
    def _compute_get_hours(self):
        for this in self:
            if this.type == 'Task':
                this.effective_hours = sum([i.complete_work_hour for i in this.task_update_ids])
                this.planned_hours = this.task_update_ids[-1].original_estimate_hour if this.task_update_ids else 0.0
                this.remaining_hours = this.task_update_ids[-1].remaining_work_hour if this.task_update_ids else 0.0
            else:
                this.planned_hours = sum([i.planned_hours for i in this.child_ids])
                this.effective_hours = sum([i.effective_hours for i in this.child_ids])
                this.remaining_hours = sum([i.remaining_hours for i in this.child_ids])
                this.total_hours_spent = this.effective_hours + this.remaining_hours
            if this.stage_id.name in ['Closed', 'Removed', 'Resolved', 'Verified']:
                this.progress = 100
            else:
                this.progress = (this.effective_hours * 100) / (
                        this.effective_hours + this.remaining_hours) if this.effective_hours + this.remaining_hours > 0 else 0

