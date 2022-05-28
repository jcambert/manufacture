# -*- coding: utf-8 -*-
from odoo import models, fields, api
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
    sequence = fields.Integer(string='Sequence',default=1,help="Ordering sequence")

    @api.model
    def seq_next_by_code(self,name=''):
        return self.env['ir.sequence'].next_by_code(name or self._sequence_name or self._name)

    @api.model
    def create(self,vals):
        seq=self.seq_next_by_code()
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