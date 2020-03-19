from odoo import models,api,fields


class Forecasting(models.Model):
    _name = 'project.forecasting'
    _description = 'Forecasting'

    from_date = fields.Date(string='From Date', required=False)
    to_date = fields.Date(string='ToDate', required=False)
    actual_hours = fields.Float(string='Actual hours', required=False)
    billing = fields.Boolean( string='Is Billable', required=False)
    billing_percentage = fields.Float(string='Billing Percentage', required=False)
    employee_name = fields.Many2one( 'hr.employee', string=' employee_name', required=False)
    project_id = fields.Many2one('project.project', string="Project")