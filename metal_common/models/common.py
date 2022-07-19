# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from random import randint
from ast import literal_eval as _literal_eval
import logging

_logger = logging.getLogger(__name__)

def literal_eval(arg):
    if isinstance(arg,bool):
        return arg
    return _literal_eval(arg)

class Model(models.AbstractModel):
    """ Main super-class for regular database-persisted Odoo models.
    Odoo models are created by inheriting from this class::
        class user(Model):
            ...
    The system will later instantiate the class once per database (on
    which the class' module is installed).
    """
    _auto = False                # automatically create database backend
    _register = False           # not visible in ORM registry, meant to be python-inherited only
    _abstract = False           # not abstract
    _transient = False          # not transient
    _name = 'model.mixin'
    _models= {}
    # @classmethod
    # def _build_model(self, pool, cr):
    #     super(models.AbstractModel,self)._build_model(pool,cr)
    #     self._models.update(_inner_models)
    def get_param(self,key):
        return literal_eval( self.env['ir.config_parameter'].get_param(key) or False)

    def __getattr__(self,key):
        # print(key)
        try:
            if isinstance(key,str) and key in self._models:
                return self.env[self._models[key]]
            res =super(models.AbstractModel,self).__getattr__(key)
        except AttributeError as ex:
            print(ex)
            print(key)


    def map(self,fn):
        return map(fn,self)
        
class BaseArchive(models.AbstractModel):
    _name='archive.mixin'
    _description='Archive Mixin'
    _inherit = ['model.mixin']
    active = fields.Boolean('Active',default=True)

    @api.model
    def do_archive(self):
        for rec in self:
            rec.active = True

class BaseSequence(models.AbstractModel):
    _name='sequence.mixin'
    _description='Sequence Mixin'
    _inherit = ['model.mixin']
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
    _inherit = ['model.mixin']
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

class BaseCompanyCurrency(models.AbstractModel):
    _name='company.currency.mixin'
    _description='Company Mixin'
    _inherit=['company.mixin']
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True,store=True)

class BaseColor(models.AbstractModel):
    _name='color.mixin'
    _description='Color Mixin'
    _inherit = ['model.mixin']
    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color Index', default=_get_default_color)

class BaseKanbanState(models.AbstractModel):
    _name='kanban.mixin'
    _description='kanban Mixin'
    _inherit = ['model.mixin']
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)
    kanban_state_label=fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', copy=False)
    
    

    def _compute_kanban_state_label(self):
        for rec in self:
            rec.kanban_state_label=rec.kanban_state

class BasteState(models.AbstractModel):
    _name='state.mixin'
    _description='State Mixin'
    _inherit = ['model.mixin']
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done','Done'),
        ('locked', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

class BasePriority(models.AbstractModel):
    _name='priority.mixin'
    _description='Priority Mixin'
    _inherit = ['model.mixin']
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True, string="Priority")