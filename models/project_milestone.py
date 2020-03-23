from odoo import models, fields, api


class Milestone(models.Model):
    _name = "project.milestone"

    start_date = fields.Date()
    name = fields.Char()
    amount = fields.Float()
    expected_delivery_date = fields.Date()
    actual_delivery_date = fields.Date()
    status = fields.Selection([('not_invoiced', 'not Invoiced'), ('invoiced', 'invoiced')], default='not_invoiced')
    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference', related='invoice_line_id.invoice_id',
                                 ondelete="set null", index=True, readonly=True)
    invoice_line_id = fields.Many2one('account.invoice.line', string='Invoice Line', store=True, readonly=1)
    approval_date = fields.Date()
    project_id = fields.Many2one('project.project', string="Project")
