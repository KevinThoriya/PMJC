from odoo import fields, models, api

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
