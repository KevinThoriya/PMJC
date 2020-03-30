from odoo import fields, api, models

class ProjectMid(models.TransientModel):
    # _inherit = 'project.project'
    _name = "project.covert"

    name = fields.Char(string="Name")
    project_id = fields.Integer(string="Project")
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="Project Manager")
    group_id = fields.Many2one('project.group', string="Group")
    billing_rate = fields.Float(string="Billing Rate")
    actual_rate = fields.Float(string="Actual Rate")

    @api.model
    def default_get(self, fields):
        res = super(ProjectMid, self).default_get(fields)
        ref_project_id = self._context.get('active_id')
        if ref_project_id:
            project = self.env['project.project'].browse(ref_project_id)
            res.update({
                'name': project.name,
                'partner_id' : project.partner_id.id,
                'user_id': project.user_id.id,
                'group_id': project.partner_id.group_id.id,
                'project_id': project.id
            })
        return res

    def covert_project(self):
        project = self.env['project.project'].browse(self.project_id)
        project.write({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'group_id': self.group_id.id,
            'state': 'project',
            'billing_rate': self.billing_rate,
            'actual_rate': self.actual_rate,
            'approved_rate_ids': [(0, 0, {'unit_of_measure': 'hour', 'rate': self.billing_rate})]
        })
