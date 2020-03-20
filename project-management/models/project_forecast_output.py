from odoo import fields, models, api
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import numpy
import pandas as pd
import statsmodels.api as sm


class ForecastingOutput (models.TransientModel):
    _name = 'project.forecasting.output'
    _description = 'Project Forecasting'

    project_id = fields.Many2one(comodel_name='project.project', string='Project')
    employee_id = fields.Many2one(comodel_name='hr.employee',string=' employee')
    date = fields.Date(string='Date')
    iteration=fields.Char("Iteration")
    week = fields.Char(string='Week')
    actual_hours = fields.Float(string='Actual hours')
    actual_amount = fields.Float(string='Actual Amount')
    is_billable = fields.Boolean(string='is billable')
    billing_percent = fields.Integer(string='Billing percent')
    billing_hour = fields.Float(string='Billing hour')
    billing_amount = fields.Float(string='Billing amount')
    type = fields.Selection(string='Type',selection=[('future', 'future'),('actual', 'actual')])

    def get_forecast(self):
        self.search([]).unlink()
        forecast_input = self.env['project.forecasting.input'].search([])
        print("----------", forecast_input)
        for current_input in forecast_input:
            employee=current_input.employee_id
            start = datetime.datetime.strptime(current_input.from_date,DATE_FORMAT)
            end = datetime.datetime.strptime(current_input.to_date,DATE_FORMAT)

            timesheets = self.env['account.analytic.line'].search([('employee_id', '=', employee.id),('project_id', '=', current_input.project_id.id)])
            print(timesheets)
            for t_data in timesheets:
                self.create({
                    'project_id': t_data.project_id.id,
                    'employee_id': t_data.employee_id.id,
                    'date': t_data.date,
                    'iteration': t_data.iteration,
                    'week': t_data.week,
                    'actual_hour': t_data.unit_amount,
                    'actual_amount': t_data.amount,
                    'is_billable': t_data.is_billable,
                    'billing_percent': t_data.billing_percent,
                    'billing_hour': t_data.billing_hour,
                    'billing_amount': t_data.billing_amount,
                    'type': 'actual'

                })


        view_id = self.env['ir.model.data'].get_object_reference('project_management', 'forecast_output_view_tree')[1]
        return {
            'name': ('Forecasting output'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': view_id,
            'res_model': 'project.forecasting.output'
        }







