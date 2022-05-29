# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class EcoStage(models.Model):
    _name = 'mrp.plm.eco.stage'
    _description = 'Eco Stage'
    _inherit = ['sequence.mixin']
    _order = "sequence, id"
    allow_apply_change = fields.Boolean('Allow apply changes', help='Is this step allowing made changes')
    approval_roles = fields.Char('Approval Roles', compute='_compute_approval_roles', store=True)
    approval_template_ids=fields.One2many('mrp.plm.eco.approval.template','stage_id',string="Stage Templates")
    final_stage = fields.Boolean('Final stage', help='Is this stage final')
    fold = fields.Boolean('fold in Kanban view',help='Is this stage folded in kanban view')
    is_blocking = fields.Boolean('Block stage', compute='_compute_is_blocking', readonly=True, help='Is this stage blocked')
    name = fields.Char('Name', required=True, translate=True)
    type_id = fields.Many2one('mrp.plm.eco.type', 'Type', required=True, ondelete='restrict')

    def _compute_approval_roles(self):
        for record in self:
            record.approval_roles = ''

    def _compute_is_blocking(self):
        for record in self:
            record.is_blocking = False

    def name_get(self):
        return [(stage.id,  stage.name  ) for stage in self]

    @api.constrains('approval_template_ids','final_stage')
    def check_approval_template_ids_final_stage(self):
        for record in self:
            if record.final_stage and len(record.approval_template_ids)>0:
                raise ValidationError("A final stage cannot have approvals")