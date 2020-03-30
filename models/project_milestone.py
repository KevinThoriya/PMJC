from odoo import models, fields, api


class Milestone(models.Model):
    _name = "project.milestone"

    name = fields.Char(string="Name", required=True)
    start_date = fields.Date(string="Start Date", default=fields.Date.context_today)
    amount = fields.Float(string="Amount", required=True)
    expected_delivery_date = fields.Date(string="Expected Delivery Date")
    actual_delivery_date = fields.Date(string="Actual Delivery Date")
    status = fields.Selection([('not_invoiced', 'Not Invoiced'), ('invoiced', 'Invoiced')], string="Status", default='not_invoiced')
    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference', related='invoice_line_id.invoice_id',
                                 ondelete="set null", index=True, readonly=True)
    invoice_line_id = fields.Many2one('account.invoice.line', string='Invoice Line', store=True, readonly=1)
    approval_date = fields.Date(string="Approval Date")
    project_id = fields.Many2one('project.project', string="Project", ondelete="set null")
