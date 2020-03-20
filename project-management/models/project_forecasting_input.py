from odoo import fields, models, api
from datetime import datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

class ForecastingInput (models.Model):
    _name = 'project.forecasting.input'
    _description = 'Forecasting Input'


    is_selectable = fields.Boolean(string="select",default=True)
    employee_id = fields.Many2one(comodel_name='hr.employee',string='Employee',required=True)
    project_id = fields.Many2one(comodel_name='project.project',string='Project',required=True)
    from_date = fields.Date(string='From Date',required=True)
    to_date = fields.Date(string='To Date',required=True)
    actual_hours = fields.Float(string='Actual hours',required=True)
    billing = fields.Boolean(string='Is Billable',required=False,default=0)
    billing_percentage = fields.Float(string='Billing Percentage',required=False,default=0)


    @api.model
    def create(self, values):
        from_date_obj=datetime.strptime(values.get('from_date'),DATE_FORMAT)
        if(values.get('from_date')>=values.get('to_date')):
            raise ValueError("from date should be less than to date")
        elif(from_date_obj.date()<datetime.today().date()):
            raise ValueError("from date should not be past date")
        else:
            return super(ForecastingInput, self).create(values)

    @api.onchange('billing')
    def onchange_method(self):
        if(self.billing==True):
            self.billing_percentage = 100
        else:
            self.billing_percentage = 0



