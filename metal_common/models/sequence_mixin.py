# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
class SequenceMixin(models.AbstractModel):
    _name='we.sequence.mixin'
    _description='Sequence Mixin'
    # _inherit = ['model.mixin']
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
        res=super(SequenceMixin,self).create(vals)
        return res