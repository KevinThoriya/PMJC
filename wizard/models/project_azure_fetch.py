from odoo import api, fields, models
import datetime


class ProjectAzure(models.TransientModel):
    _name = "project.azure"

    project_id = fields.Many2one('project.project', string="Project")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date", default=fields.Date.context_today)

    def fetch_workitem(self):
        # COLLECT ALL WORKITEMS
        params = self.env['ir.config_parameter'].sudo()
        start = datetime.datetime.strptime(self.start_date, "%Y-%m-%d") if self.start_date else False
        end = datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
        web = params.get_param('azure.web.address')
        pat = params.get_param('azure.token')
        project = self.project_id
        self.env['project.project'].with_delay(priority=1).get_workitems_of_project(project, web, pat, start, end)
