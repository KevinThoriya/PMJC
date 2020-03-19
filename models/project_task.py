from odoo import models, fields, api
from . import tools
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
    def _compute_week(selfs):
        for self in selfs:
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
                this.remaining_hours = this.task_update_ids[
                    -1].remaining_work_hour if this.task_update_ids else 0.0  # sum([i.remaining_work_hour for i in this.task_update_ids])
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

    def get_azure_data(self):

        def get_emp(ar, project):
            """
            :param ar: array contain [<name>,<email>]
            :return :odoo id of res user
            """
            if not ar: return None
            emp = self.env['res.users'].search([('login', '=', ar[1])])
            if emp:
                return emp[0].id
            else:
                emp = self.env['res.users'].create(
                    {'name': ar[0], 'login': ar[1], 'password': '123'})

                emp.employee_id.project_ids = [(4, project.id, None)]  # adding extry in employee field of project

                self.env['project.cost.rate'].create({
                    'project_id': project.id, 'employee_id': emp.employee_id.id,
                    'cost_rate': project.billing_rate, 'is_billable': True,
                    'billing_percent': 100
                })  # adding entry in cost rate model for all the employee related to that project
                return emp.id

        def store_odoo(all_workitem):
            """
            :param all_workitem: contain list of dict of azure data.
            """
            # ITRATE EVERY WORKITEMS AND CREATE BY ODOO
            for workitem in all_workitem:
                # FIND AND SET PERENT IF ANY THERE
                parent_obj = self.env['project.task'].search([('azure_id', '=', workitem['parent_task_id'])],
                                                             order="create_date desc")
                if parent_obj:
                    workitem['parent_task_id'] = parent_obj[0].id
                    workitem['color'] = 3
                else:
                    workitem['parent_task_id'] = False
                    workitem['color'] = 7
                # FIND AND SET ALL THE CHILDRENS ------> "DONT NEED OF CHILD _ONLY PERENT IS ENUGH "
                # childs = []
                # for i in workitem['child_ids']:
                #     child_obj = self.env['project.task'].search([('azure_id', '=', i)],order="create_date desc")
                #     if child_obj:
                #         childs.append(child_obj[0].id)
                # workitem['child_ids'] = [[6, 0, childs]]

                # setting the project

                project = self.env['project.project'].search([('name', '=', workitem['project_id'])], limit=1)
                if project:
                    workitem['project_id'] = project[0].id
                else:
                    project = self.env['project.project'].create(
                        {'name': workitem['project_id']})
                    workitem['project_id'] = project.id

                # setting employee create new is not assigning to RES.USERS
                workitem['user_id'] = get_emp(workitem['user_id'], project)
                workitem['created_by_id'] = get_emp(workitem['created_by_id'], project)
                workitem['changed_by_id'] = get_emp(workitem['changed_by_id'], project)

                # setting the stage
                if self.azure_id == 13005: print("here next ....")
                if self.azure_id == 13054: print(workitem['stage_id'])
                stage = self.env['project.task.type'].search([('name', '=', workitem['stage_id'])], limit=1)
                if stage:
                    if self.azure_id == 13054: print("stage", stage)
                    workitem['stage_id'] = stage[0].id
                else:
                    res = self.env['project.task.type'].create({'name': workitem['stage_id'], 'fold': False,
                                                                'description': 'Azure Creation '})
                    workitem['stage_id'] = res.id
                    if self.azure_id == 13054: print(res)
                # setting Iteration to Tasks :
                iteration_id = self.env['project.iteration'].search([('azure_id', '=', workitem['iteration_id']),
                                                                     ('project_id', '=', workitem['project_id'])])
                if iteration_id:
                    workitem['iteration_id'] = iteration_id[0].id
                else:
                    res = self.env['project.iteration'].create(
                        {'name': workitem['iteration_path'], 'azure_id': workitem['iteration_id'],
                         'project_id': workitem['project_id']})
                    workitem['iteration_id'] = res.id
                # setting areapath to Tasks :
                areapath_id = self.env['project.areapath'].search([('name', '=', workitem['areapath_id']),
                                                                   ('project_id', '=', workitem['project_id'])])
                if areapath_id:
                    workitem['areapath_id'] = areapath_id[0].id
                else:
                    res = self.env['project.areapath'].create(
                        {'name': workitem['areapath_id'], 'project_id': workitem['project_id']})
                    workitem['areapath_id'] = res.id

                # create or update the tasks
                odoo_rec = self.env['project.task'].search([('azure_id', '=', workitem['azure_id'])],
                                                           order="create_date desc", limit=1)

                task_dict = {'azure_id': workitem['azure_id'], 'areapath_id': workitem['areapath_id'],
                             'iteration_path': workitem['iteration_path'],
                             'iteration_id': workitem['iteration_id'], 'user_id': workitem['user_id'],
                             'reason': workitem['reason'],
                             'created_date': workitem['created_date'], 'created_by_id': workitem['created_by_id'],
                             'priority': workitem['priority'], 'color': workitem['color'],
                             'title': workitem['title'], 'name': workitem['name'],
                             'description': workitem['description'], 'parent_task_id': workitem['parent_task_id'],
                             'type': workitem['type'], 'project_id': workitem['project_id'],
                             'stage_id': workitem['stage_id'],
                             }
                task_update_dict = {'changed_date': workitem['changed_date'],
                                    'changed_by_id': workitem['changed_by_id'],
                                    'original_estimate_hour': workitem['original_estimate_hour'],
                                    'remaining_work_hour': workitem['remaining_work_hour'],
                                    'complete_work_hour': workitem['complete_work_hour'], }

                if odoo_rec:
                    odoo_rec[0].write(task_dict)
                    updates = self.env['project.task.update'].search([('task_id', '=', odoo_rec[0].id)],
                                                                     order="create_date desc")

                    total_comp_hour = sum([i.complete_work_hour for i in updates])
                    task_update_dict.update({'task_id': odoo_rec[0].id})

                    if (updates
                            and (workitem['original_estimate_hour'] != updates[0].original_estimate_hour
                                 or workitem['complete_work_hour'] != total_comp_hour)):
                        if odoo_rec[0].stage_id.name == 'New':
                            updates[0].write(task_update_dict)
                        else:
                            task_update_dict['complete_work_hour'] -= updates[0].complete_work_hour
                            self.env['project.task.update'].create(task_update_dict)
                else:
                    res = self.env['project.task'].create(task_dict)
                    task_update_dict.update({'task_id': res.id})
                    self.env['project.task.update'].create(task_update_dict)

        # COLLECT ALL WORKITEMS
        params = self.env['ir.config_parameter'].sudo()
        start = datetime.datetime.strptime(params.get_param('azure.last.backup.date'), "%Y-%m-%d")
        end = datetime.datetime.today().strftime('%Y-%m-%d')

        for project in self.env['project.project'].search([]):
            all_workitem = tools.work_items(params.get_param('azure.web.address'), params.get_param('azure.token'),
                                            project=project.name, start_date=start, end_date=end, on="CreatedDate",
                                            on2="ChangedDate")
            store_odoo(all_workitem)
        # params.set_param('azure.last.backup.date', end)
