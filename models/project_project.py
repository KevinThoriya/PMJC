from odoo import models, fields, api
from odoo.addons.queue_job.job import job
from . import tools
import datetime


class ProjectGroup(models.Model):
    _name = "project.group"

    name = fields.Char(string="Name of Group", required=True)
    active = fields.Boolean(string="active", default=True)


class CostRate(models.Model):
    _name = "project.cost.rate"
    _description = 'CostRate'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    cost_rate = fields.Integer(string="Cost Rate", required=True)
    is_billable = fields.Boolean(string="is Billable ?")
    billing_percent = fields.Integer(string='Billing %', required=True)
    project_id = fields.Many2one('project.project', string="Project", ondelete='cascade')


class ApprovedRate(models.Model):
    _name = "project.approved.rate"
    _description = 'ApprovedRate'

    unit_of_measure = fields.Selection(string="Unit of Measure",
                                       selection=[('week', 'By Week'), ('hour', 'By Hour'), ('month', 'By Month')], required=True)
    rate = fields.Float(string="Rate", required=True)
    project_id = fields.Many2one('project.project', string="project", ondelete='cascade')


class Project(models.Model):
    _inherit = "project.project"

    group_id = fields.Many2one('project.group', string="Project Group")
    start_date = fields.Date( string="Start Date", default=fields.Date.context_today)
    expected_end_date = fields.Date(string="Expected EndDate")
    expiration_date = fields.Date(string="Expiration Date")
    priority = fields.Selection(string="priority", selection=[('0', 'Low'), ('1', 'Medium'), ('2', 'High')], default='1')
    milestone_ids = fields.One2many('project.milestone', 'project_id', string='Milestones')
    employee_ids = fields.Many2many("hr.employee", 'rel_project_employee', 'project_id', 'emp_id', string="Employees")
    iteration_ids = fields.One2many('project.iteration', 'project_id', string="Iterations")
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount = fields.Monetary(currency_field='currency_id', string="Amount")
    billing_rate = fields.Float(string="Billing Rate (Hour)")
    actual_rate = fields.Float(string="Cost Rate (Hour)")
    cost_rate_ids = fields.One2many('project.cost.rate', 'project_id', string="Cost Rate By Employee")
    approved_rate_ids = fields.One2many('project.approved.rate', 'project_id', string="Approved Rate")
    unit_of_measure = fields.Selection(string="Default Unit of Measure", selection=[('week', 'By Week'), ('hour', 'By Hour'), ('fixed', 'Fixed')], default="hour")
    timesheet_grouping = fields.Selection(selection=[('week', 'By Week'), ('iteration', 'By Iteration'), ('month', 'By Month'), ('milestone', 'By Milestone'), ('project', 'By Project'), ('no_grouping', 'No Grouping')],
                                          string="Default Timesheet Grouping", default="week")
    state = fields.Selection(string="State", selection=[('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('project', 'Project'), ('done', 'Locked'), ('cancel', 'Cancelled')], default='project')

    @api.model
    def create(self,vals):
        res = super(Project, self).create(vals)
        if res.state == 'project':
            res.write({
                'approved_rate_ids': [(0,0,{'rate': res.billing_rate, 'unit_of_measure': 'hour'})]
            })
        return res

    def get_user(self, ar, project, cost_rate_entry):
        """
        :param ar: array contain [<name>,<email>]
        :return :odoo id of res user
        """
        if not ar:
            return None
        user = self.env['res.users'].search([('login', '=', ar[1])])
        if user:  # finding user in res.user
            if not user.employee_id: # if endUser delete hr.employee
                user[0].write({
                    'employee_id': self.env['hr.employee'].create({'name': user.name, 'work_email': user.login })
                })
            if project.id not in user.employee_id.project_ids.ids:  # check that project is set for that user->emp
                user.employee_id.write({'project_ids': [(4, project.id, None)]})  # adding entry in employee field of project

            if cost_rate_entry and user.employee_id not in project.cost_rate_ids.mapped('employee_id'):
                emp_rate = self.env['project.cost.rate'].create({
                    'project_id': project.id, 'employee_id': user.employee_id.id,
                    'cost_rate': project.actual_rate, 'is_billable': True,
                    'billing_percent': 100})  # adding entry in cost rate models for the employee related to project
            return user[0].id
        else:  # res.user not found
            user = self.env['res.users'].create(
                {'name': ar[0],
                 'login': ar[1],
                 'password': '123',
                 'employee_id': self.env['hr.employee'].create({'name': ar[0],
                                                                'work_email': ar[1],
                                                                'project_ids': [(4, project.id)]}).id})
            user.partner_id.customer = False  # not a customer but employee
            if cost_rate_entry:
                emp_rate = self.env['project.cost.rate'].create({
                    'project_id': project.id, 'employee_id': user.employee_id.id,
                    'cost_rate': project.actual_rate, 'is_billable': True,
                    'billing_percent': 100})
                return user.id

    def get_stage(self, stage_id):
        stage = self.env['project.task.type'].search([('name', '=', stage_id)], limit=1)
        if stage:
            return stage[0].id
        else:
            res = self.env['project.task.type'].create({'name': stage_id, 'fold': False,
                                                        'description': 'Azure Creation '})
            return res.id
    
    def get_iteration(self, project_id, iteration_path):
        iteration = self.env['project.iteration'].search([('path', '=', iteration_path),
                                                             ('project_id', '=', project_id)])
        if iteration:
            return iteration[0].id

    def get_areapath(self, areapath_id, project_id):
        areapath = self.env['project.areapath'].search([('name', '=', areapath_id),
                                                           ('project_id', '=', project_id)])
        if areapath:
            return areapath[0].id
        else:
            res = self.env['project.areapath'].create(
                {'name': areapath_id, 'project_id': project_id})
            return res.id

    def get_child(self, child_ids):
        child_obj = self.env['project.task'].search([('azure_id', 'in', child_ids)], order="create_date desc")
        childs = [i.id for i in child_obj]
        return [[6, 0, childs]]

    @job(default_channel='root.azure_workitems.iterator.store_item')
    def store_workitem_odoo(self, workitem):
        """
        description :"store single items"
        :arg workitem: dict contains data of workitem or Task
        """
        # FIND AND SET PERENT IF ANY THERE
        parent_obj = self.env['project.task'].search([('azure_id', '=', workitem['parent_task_id'])],
                                                     order="create_date desc")
        if parent_obj:
            workitem.update({
                'parent_task_id': parent_obj[0].id,
                'color': 3
            })
        else:
            workitem.update({
                'parent_task_id': False,
                'color': 7
            })
        # setting project
        project = self.env['project.project'].search([('name', '=', workitem['project_id'])], limit=1)

        workitem.update({
            'project_id': project[0].id,
            'user_id': self.get_user(workitem['user_id'], project, True),
            'created_by_id': self.get_user(workitem['created_by_id'], project, False),
            'changed_by_id': self.get_user(workitem['changed_by_id'], project, False),
            'stage_id': self.get_stage(workitem['stage_id']),
            'iteration_id': self.get_iteration(project.id, workitem['iteration_path']),
            'areapath_id': self.get_areapath(workitem['areapath_id'], project.id),
            'child_ids': self.get_child(workitem['child_ids']),
        })

        # create or update the tasks
        odoo_rec = self.env['project.task'].search([('azure_id', '=', workitem['azure_id'])],
                                                   order="create_date desc", limit=1)

        task_dict = {'azure_id': workitem['azure_id'], 'areapath_id': workitem['areapath_id'],
                     'iteration_path': workitem['iteration_path'],
                     'iteration_id': workitem['iteration_id'], 'user_id': workitem['user_id'],
                     'reason': workitem['reason'], 'name': workitem['name'],
                     'created_date': workitem['created_date'], 'created_by_id': workitem['created_by_id'],
                     'priority': workitem['priority'], 'color': workitem['color'],
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
            task_dict.update({'task_update_ids': [(0, 0, task_update_dict)]})
            res = self.env['project.task'].create(task_dict)

    @job(default_channel='root.azure_workitems.iterator')
    def store_odoo(self, all_workitem):
        """
         description: "make a job for storing every workitems"
        :param all_workitem: contain list of dict of azure data.
        """
        # ITRATE EVERY WORKITEMS AND CREATE BY ODOO
        for workitem in all_workitem:
            self.with_delay(priority=2).store_workitem_odoo(workitem)

    @job(default_channel='root.azure_workitems')
    def get_workitems_of_project(self, project, web, pat, start, end):
        """
        description: "get project vise workitems from azure "
        """
        all_workitems = tools.work_items(web, pat, project=project.name, start_date=start, end_date=end,
                                         on="CreatedDate", on2="ChangedDate")
        self.with_delay(priority=2).store_odoo(all_workitems)

    @job(default_channel='root.iteration')
    def get_and_store_iteration(self, project):
        iterations = tools.get_all_iteration(web, pat, project.name)
        for iteration in iterations:
            iter_odoo = self.env['project.iteration'].search([('azure_id', '=', iteration['id'])])
            if iter_odoo:
                iter_odoo[0].write(iteration)
            else:
                project.write({
                    'iteration_ids' : [0, 0, iteration]
                })

    def get_azure_data(self):
        # COLLECT ALL WORKITEMS
        params = self.env['ir.config_parameter'].sudo()
        web = params.get_param('azure.web.address')
        pat = params.get_param('azure.token')
        start = datetime.datetime.strptime(params.get_param('azure.last.backup.date'), "%Y-%m-%d")
        end = datetime.datetime.today().strftime('%Y-%m-%d')

        for project in self.env['project.project'].search([('state', '=', 'project')]):
            self.with_delay(priority=1).get_and_store_iteration(project)
            self.with_delay(priority=2).get_workitems_of_project(project, web, pat, start, end)
        params.set_param('azure.last.backup.date', end)
