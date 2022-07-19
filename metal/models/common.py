# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from random import randint

class BaseArchive(models.AbstractModel):
    _name='archive.mixin'
    _description='Archive Mixin'
    active = fields.Boolean('Active',default=True)

    def do_archive(self):
        for rec in self:
            rec.active = True

class BaseSequence(models.AbstractModel):
    _name='sequence.mixin'
    _description='Sequence Mixin'
    _sequence_name=''
    sequence = fields.Char(string='Sequence',default=1,help="Ordering sequence")

    @api.model
    def seq_next_by_code(self,name=''):
        return self.env['ir.sequence'].next_by_code(name or self._sequence_name or self._name)

    @api.model
    def create(self,vals):
        seq=self.seq_next_by_code()
        if int(self.sequence)==self.sequence:
            vals['sequence']=seq
        else:
            if vals.get('sequence',_('New'))==_('New'):
                vals['sequence']=(seq or _('New')) 
            elif seq:
                vals['sequence']=seq
        res=super(BaseSequence,self).create(vals)
        return res

class BaseCompany(models.AbstractModel):
    _name='company.mixin'
    _description='Company Mixin'
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

class BaseColor(models.AbstractModel):
    _name='color.mixin'
    _description='Color Mixin'
    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color Index', default=_get_default_color)

class BaseKanbanState(models.AbstractModel):
    _name='kanban.mixin'
    _description='kanban Mixin'

    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)
    kanban_state_label=fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', copy=False)
    
    

    def _compute_kanban_state_label(self):
        for rec in self:
            rec.kanban_state_label=rec.kanban_state

class BasePriority(models.AbstractModel):
    _name='priority.mixin'
    _description='Priority Mixin'

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True, string="Priority")