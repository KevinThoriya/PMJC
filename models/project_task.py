from odoo import models, fields, api
import datetime


class ProjectAreapath(models.Model):
    _name = "project.areapath"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    project_id = fields.Many2one('project.project', string="Project Name", ondelete='cascade')


class ProjectIteration(models.Model):
    _name = "project.iteration"

    name = fields.Char(string="name", required=True)
    azure_id = fields.Char(string="Azure Id")
    path = fields.Char(string="Path")
    active = fields.Boolean(string="Active", default=True)
    startdate = fields.Date(string="Start Date", default=fields.Date.context_today)
    enddate = fields.Date(string="End Date")
    time_frame = fields.Char(string="Time Frame")
    project_id = fields.Many2one('project.project', string="Project Name", ondelete='cascade')


class ProjectTaskUpdate(models.Model):
    _name = "project.task.update"

    changed_date = fields.Date(string="Change Date",index=True)
    changed_by_id = fields.Many2one('res.users', string='Changed By')
    remaining_work_hour = fields.Float(string="Remaining Work Hours")
    original_estimate_hour = fields.Float(string="Original Estimate Hours")
    complete_work_hour = fields.Float(string="Completed Work Hours")
    task_id = fields.Many2one("project.task", string="Task Name", ondelete='cascade')


class ProjectTask(models.Model):
    _inherit = "project.task"

    azure_id = fields.Char(string="Azure Id", index=True)
    areapath_id = fields.Many2one('project.areapath', string="AreaPath")
    iteration_path = fields.Char(string="Iteration Path")
    iteration_id = fields.Many2one('project.iteration', string="Iteration")
    week = fields.Char(compute="_compute_week", store=True, string="Week")
    emp_id = fields.Many2one('hr.employee', string="Employee Assigned To", related='user_id.employee_id', store=True)
    user_id = fields.Many2one('res.users', string='Assigned to', index=True, track_visibility=False, default=False,
                              related=False, store=True)
    reason = fields.Char(string="Reason")
    created_date = fields.Date(string="Create Date", index=True)
    created_by_id = fields.Many2one('res.users', string='Created By')
    priority = fields.Selection(selection=[(4, 4), (3, 3), (2, 2), (1, 1),], default='1', string="Priority")
    description = fields.Html(string="Description")
    parent_task_id = fields.Many2one('project.task', string='Parent Task')
    child_ids = fields.One2many('project.task', 'parent_task_id', string='Child Tasks', domain=[('active', '=', True)], ondelete='cascade')
    type = fields.Selection(selection=[('Bug', 'Bug'), ('Code Review Request', 'Code Review Request'),
                                       ('Code Review Response', 'Code Review Response'),
                                       ('Epic', 'Epic'), ('Feature', 'Feature'),
                                       ('Feedback Request', 'Feedback Request'),
                                       ('Feedback Response', 'Feedback Response'), ('Shared Steps', 'Shared Steps'),
                                       ('Test Case', 'Test Case'),
                                       ('Test Plan', 'Test Plan'), ('Test Suite', 'Test Suite'),
                                       ('User Story', 'User Story'), ('Issue', 'Issue'),
                                       ('Shared Parameter', 'Shared Parameter'), ('Task', 'Task'),
                                       ('Change Request', 'Change Request')], string="Type")
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

    @api.model
    def name_get(self):
        result = []
        for i in self:
            result.append((i.id, f"{i.type} {i.azure_id}- {i.name}"))
        return result
