from odoo import fields, models, api


class ProjectExpense(models.Model):
    _name = 'project.expense'
    _description = 'Project Expenses'

    date = fields.Date(string='create date',required=True)
    name = fields.Char(string='Expense Description',required=True)
    project_id = fields.Many2one(comodel_name='project.project',string='Project',required=True)
    quantity = fields.Integer(string='Quantity',default="1")
    cost_price = fields.Float(string='Cost price',required=True,default=10000)
    is_billable = fields.Boolean(string='Is billable')
    billing_amount = fields.Float(string='Billing amount',required=False)
    generate_date = fields.Date(string='Generate_date',required=False)
    status = fields.Selection(string='Status',selection=[('invoiced', 'Invoiced'),('not_invoiced', 'Not Invoiced')],required=False)
    invoice = fields.Char(string='Invoice',required=False)
    invoice_line = fields.Char(string='Invoice line',required=False)
    ref_no = fields.Char(string='Ref_no', required=False)
    vendor = fields.Char(string='Vendor', required=False)
    attachment = fields.Many2many(comodel_name='ir.attachment',relation="m2m_ir_attachment_expenses",string='Attachment')


class ProjectAttachment(models.Model):
    _inherit = 'ir.attachment'

    expense_id = fields.Many2one(comodel_name='project.expense',string='Expense',required=False)




