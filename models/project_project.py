from odoo import models, fields, api
from . import tools
import datetime


class ProjectGroup(models.Model):
    _name = "project.group"

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


class Project(models.Model):
    _inherit = "project.project"

    group_id = fields.Many2one('project.group', string="Project Group")
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
    actual_rate = fields.Float(string="Cost Rate")
    cost_rate_ids = fields.One2many('project.cost.rate', 'project_id', string="Cost Rate By Employee")
    approved_rate_ids = fields.One2many('project.approved.rate', 'project_id', string="Approved Rate")
    unit_of_measure = fields.Selection(string="Default Unit of Measure", selection=[('week', 'By Week'), ('hour', 'By Hour'), ('month', 'By Month')])
    timesheet_grouping = fields.Selection(string="Default Timesheet Grouping", selection=[('week', 'By Week'), ('hour', 'By Hour'), ('month', 'By Month')])
    state = fields.Selection([('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('project', 'Project'), ('done', 'Locked'), ('cancel', 'Cancelled')], default='draft')

    @api.model
    def create(self, val):
        res = super(Project, self).create(val)
        #  this should be run when qoutation is change to project
        self.env['project.approved.rate'].create({'unit_of_measure':  'hour', 'rate': res.billing_rate, 'project_id': res.id})
        return res

    def get_user(self, ar, project):
        """
        :param ar: array contain [<name>,<email>]
        :return :odoo id of res user
        """
        if not ar:
            return None
        user = self.env['res.users'].search([('login', '=', ar[1])])
        if user:  # finding user in res.user
            if not user.employee_id: # if end_user delete hr.employee
                emp = self.env['hr.employee'].create(
                    {'name': user.name, 'work_email': user.login, 'user_id': user.id})
                user.employee_id = emp.id  # setting new employee in hr.employee

            if not project.id in [i.id for i in user.employee_id.project_ids]:  # check that project is set for that user->emp
                emp = user.employee_id
                emp_rate = self.env['project.cost.rate'].create({
                    'project_id': project.id, 'employee_id': emp.id,
                    'cost_rate': project.actual_rate, 'is_billable': True,
                    'billing_percent': 100
                })  # adding entry in cost rate models for the employee related to that project
                emp.project_ids = [(4, project.id, None)]  # adding entry in employee field of project

            return user[0].id

        else:  # res.user not found
            user = self.env['res.users'].create(
                {'name': ar[0], 'login': ar[1], 'password': '123'})

            emp_rate = self.env['project.cost.rate'].create({
                'project_id': project.id, 'employee_id': user.employee_id.id,
                'cost_rate': project.actual_rate, 'is_billable': True,
                'billing_percent': 100
            })  # adding entry in cost rate models for all the employee related to that project
            user.employee_id.project_ids = [(4, project.id, None)]  # adding extry in employee field of project

            return user.id

    def store_odoo(self, all_workitem):
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

            project = self.env['project.project'].search([('name', '=', workitem['project_id'])], limit=1)
            if project:
                workitem['project_id'] = project[0].id
            else:
                project = self.env['project.project'].create(
                    {'name': workitem['project_id']})
                workitem['project_id'] = project.id

            # setting employee create new is not assigning to RES.USERS
            workitem['user_id'] = self.get_user(workitem['user_id'], project)
            workitem['created_by_id'] = self.get_user(workitem['created_by_id'], project)
            workitem['changed_by_id'] = self.get_user(workitem['changed_by_id'], project)

            # setting the stage
            stage = self.env['project.task.type'].search([('name', '=', workitem['stage_id'])], limit=1)
            if stage:
                workitem['stage_id'] = stage[0].id
            else:
                res = self.env['project.task.type'].create({'name': workitem['stage_id'], 'fold': False,
                                                            'description': 'Azure Creation '})
                workitem['stage_id'] = res.id
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

    def get_azure_data(self):
        # COLLECT ALL WORKITEMS
        params = self.env['ir.config_parameter'].sudo()
        start = datetime.datetime.strptime(params.get_param('azure.last.backup.date'), "%Y-%m-%d")
        end = datetime.datetime.today().strftime('%Y-%m-%d')

        for project in self.env['project.project'].search([]):
            all_workitems = tools.work_items(params.get_param('azure.web.address'), params.get_param('azure.token'),
                                            project=project.name, start_date=start, end_date=end, on="CreatedDate",
                                            on2="ChangedDate")
            self.store_odoo(all_workitems)
        # params.set_param('azure.last.backup.date', end)




