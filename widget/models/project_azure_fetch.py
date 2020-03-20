from odoo import api, fields, models
import datetime
from odoo.addons.aproject.models import tools


class ProjectAzure(models.TransientModel):
    _name = "project.azure"

    project_id = fields.Many2one('project.project', string="Project")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date", default=fields.Date.context_today)

    def fetch_workitem(self):
        # COLLECT ALL WORKITEMS
        params = self.env['ir.config_parameter'].sudo()
        start = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(self.end_date, "%Y-%m-%d")

        all_workitems = tools.work_items(params.get_param('azure.web.address'), params.get_param('azure.token'),
                                         project=self.project_id.name, start_date=start, end_date=end, on="CreatedDate",
                                         on2="ChangedDate")
        print(all_workitems,self.project_id.name,start,end )
        self.env['project.project'].store_odoo(all_workitems)
        # params.set_param('azure.last.backup.date', end) # do not set here
