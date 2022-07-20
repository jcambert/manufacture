# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
class BaseKanbanState(models.AbstractModel):
    _name='we.kanban.mixin'
    _description='kanban Mixin'
    # _inherit = ['model.mixin']
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)
    kanban_state_label=fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', copy=False)
    
    

    def _compute_kanban_state_label(self):
        for rec in self:
            rec.kanban_state_label=rec.kanban_state