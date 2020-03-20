from odoo import fields, models, api
from datetime import datetime,timedelta
import calendar
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class ProjectRecurringExpense (models.Model):
    _name = 'project.recurring.expense'
    _description = 'Recurring Expenses'

    project_id = fields.Many2one(comodel_name='project.project',string='Project',required=True)
    start_date = fields.Date(string='Start Date',required=True)
    end_date = fields.Date(string='End Date',required=True)
    name = fields.Char(string='Expense Description',required=True)
    quantity = fields.Integer(string='Quantity',required=False,default="1")
    cost_price = fields.Float(string='Cost price',required=True,default=10000)
    is_billable = fields.Boolean(string='Is billable',required=False)
    billing_amount = fields.Float(string='Billing amount',required=False)
    recurring_mode = fields.Selection(string='Recurring mode',selection=[('weeks', 'weeks'),('months', 'months'),('years', 'years')],required=True)
    last_generated_date = fields.Date(string='Last Generated date',required=False)

    def auto_generate_expenses(self):
        print("Fetching Recurring Expenses to update Expense!!!")
        recurringExpenses = self.env['project.recurring.expense'].search([])

        for record in recurringExpenses:
            update = None
            if (datetime.strptime(record.start_date, DATE_FORMAT).date() == datetime.today().date()):
                update = datetime.today().date()

            else:
                if (record.last_generated_date != False):
                    if (record.last_generated_date != record.end_date):
                        print("recurring expense => ",record.name,"last generated date => ",record.last_generated_date)
                        last_generated_date_obj = datetime.strptime(record.last_generated_date, DATE_FORMAT)
                        if (record.recurring_mode == "months"):
                            days_in_months = calendar.monthrange(last_generated_date_obj.year, last_generated_date_obj.month)[1]
                            update = (last_generated_date_obj + timedelta(days=days_in_months)).date()

                        elif (record.recurring_mode == "weeks"):
                            update = (last_generated_date_obj + timedelta(weeks=1)).date()

                        elif (record.recurring_mode == "years"):
                            update = (last_generated_date_obj + timedelta(days=365)).date()

                else:
                    print("Updating Past Entries!!!")
                    self.update_past_entries(record)


            if (update != None):
                if (update == datetime.today().date()):
                    vals = {
                        'date':datetime.today().date(),
                        'name':record.name,
                        'project_id':record.project_id.id,
                        'quantity':record.quantity,
                        'cost_price':record.cost_price,
                        'is_billable':record.is_billable,
                        'billing_amount':record.billing_amount,
                        'generate_date':datetime.today().date(),
                        'status':'not_invoiced'
                    }
                    self.env['project.expense'].create(vals)
                    print("start date => ",record.start_date)
                    print("end date => ",record.end_date)
                    print("generated entry on => ", datetime.today().date())
                    print("last generated date => ", record.last_generated_date)
                    record.last_generated_date = update

            self.update_missing_entries(record,update)





    def update_past_entries(self,record):
        start_date_obj = datetime.strptime(record.start_date, DATE_FORMAT)
        end_date_obj = datetime.strptime(record.end_date, DATE_FORMAT)
        if (start_date_obj.date() < datetime.today().date()):
            delta = datetime.today() - start_date_obj
            print(delta)
            if (record.recurring_mode == "weeks"):
                i = 0
                print("weeks")
                while (i < delta.days):
                    print(i)
                    update = (start_date_obj + timedelta(days=i)).date()
                    print(update)
                    if (update < datetime.today().date()):
                        vals = {
                            'date': update,
                            'name': record.name,
                            'project_id': record.project_id.id,
                            'quantity': record.quantity,
                            'cost_price': record.cost_price,
                            'is_billable': record.is_billable,
                            'billing_amount': record.billing_amount,
                            'generate_date': datetime.today().date(),
                            'status': 'not_invoiced'
                        }
                        self.env['project.expense'].create(vals)
                        print("start date => ", record.start_date)
                        print("end date => ", record.end_date)
                        print("generated entry on => ", datetime.today().date())
                        print("last generated date => ", record.last_generated_date)

                        record.last_generated_date = update
                    i = i + 7
            elif (record.recurring_mode == "months"):
                print("months")
                i = 0
                days_in_months = calendar.monthrange(start_date_obj.year, start_date_obj.month)[1]
                print(days_in_months)
                print(delta.days)
                while (i < delta.days):
                    print(i)
                    update = (start_date_obj + timedelta(days=i)).date()

                    print(update)
                    if (update < datetime.today().date()):
                        vals = {
                            'date': update,
                            'name': record.name,
                            'project_id': record.project_id.id,
                            'quantity': record.quantity,
                            'cost_price': record.cost_price,
                            'is_billable': record.is_billable,
                            'billing_amount': record.billing_amount,
                            'generate_date': datetime.today().date(),
                            'status': 'not_invoiced'
                        }
                        self.env['project.expense'].create(vals)
                        print("start date => ", record.start_date)
                        print("end date => ", record.end_date)
                        print("generated entry on => ", datetime.today().date())
                        print("last generated date => ", record.last_generated_date)

                        record.last_generated_date = update
                    i = i + days_in_months

            elif (record.recurring_mode == "years"):
                print("years")
                i = 1
                while (i < delta.days):
                    print(i)
                    update = (start_date_obj + timedelta(days=i)).date()
                    print(update)
                    if (update < datetime.today().date()):
                        vals = {
                            'date': update,
                            'name': record.name,
                            'project_id': record.project_id.id,
                            'quantity': record.quantity,
                            'cost_price': record.cost_price,
                            'is_billable': record.is_billable,
                            'billing_amount': record.billing_amount,
                            'generate_date': datetime.today().date(),
                            'status': 'not_invoiced'
                        }
                        self.env['project.expense'].create(vals)
                        print("start date => ", record.start_date)
                        print("end date => ", record.end_date)
                        print("generated entry on => ", datetime.today().date())
                        print("last generated date => ", record.last_generated_date)

                        record.last_generated_date = update
                    i = i + 365


    def update_missing_entries(self,record,update):
        params = self.env['ir.config_parameter'].sudo()
        last_date=params.get_param('expense.last.backup.date')

        last_date_obj = datetime.strptime(last_date, DATE_FORMAT)
        if (last_date_obj.date() < datetime.today().date()):
            delta=datetime.today()-last_date_obj
            for i in range(1,delta.days+1):
                print(i)
                date=(last_date_obj + timedelta(days=i)).date()
                if(update==date):
                    vals = {
                        'date': datetime.today().date(),
                        'name': record.name,
                        'project_id': record.project_id.id,
                        'quantity': record.quantity,
                        'cost_price': record.cost_price,
                        'is_billable': record.is_billable,
                        'billing_amount': record.billing_amount,
                        'generate_date': datetime.today().date(),
                        'status': 'not_invoiced'
                    }
                    self.env['project.expense'].create(vals)
                    print("start date => ", record.start_date)
                    print("end date => ", record.end_date)
                    print("generated entry on => ", datetime.today().date())
                    print("last generated date => ", record.last_generated_date)
                    record.last_generated_date = update
        params.set_param('expense.last.backup.date',datetime.today().date())


    @api.model
    def create(self, values):
        if(values.get('start_date')>=values.get('end_date')):
            raise ValueError("start date should be less than end date")
        else:
            return super(ProjectRecurringExpense, self).create(values)




















