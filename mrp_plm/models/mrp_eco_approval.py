# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class EcoApproval(models.Model):
    _name='mrp.plm.eco.approval'
    _description='Eco Approval'
    _inherits = {'mrp.plm.eco.approval.template': 'approval_template_id'}
    _order="sequence desc,id"
    approval_date=fields.Datetime('Approval date')
    approval_template_id=fields.Many2one('mrp.plm.eco.approval.template',"Approval template",auto_join=True,index=True, ondelete='cascade',required=True,help="Approval template")
    eco_id=fields.Many2one('mrp.plm.eco','Technical Change',ondelete='cascade',required=True,help="Technical ECO")
    eco_stage_id=fields.Many2one(related="eco_id.stage_id",string="ECO Stage",store=True,help="ECO Stage")
    is_approved=fields.Boolean("Is approved",compute='_compute_status',store=True,readonly=True)
    is_rejected=fields.Boolean("Is rejected",compute='_compute_status',store=True,readonly=True)
    is_closed=fields.Boolean("Is closed",compute='_compute_status',store=True,readonly=True)
    
    required_user_ids=fields.Many2many('res.users',string="Utilisateurs requis",compute='_compute_required_users')
    status=fields.Selection([
        ('none','not yet'),
        ('comment','Comment'),
        ('approved','Approved'),
        ('rejected','Rejected')],'Statut',default='none',required=True)
    template_stage_id=fields.Many2one('mrp.plm.eco.stage',string='Validation stage')
    user_id=fields.Many2one('res.users','Approuvé par')

    @api.model
    @api.returns('bool')
    def has_rejected(self):
        return len(self.filtered(lambda r:r.is_rejected))>0

    @api.model
    @api.returns('bool')
    def user_can_approve(self):
        r=self.filtered(lambda r:(not r.is_approved) and (not r.is_closed)  and (self.env.user.id in r.required_user_ids.mapped('id') or self.env.is_superuser()) and (r.template_stage_id==r.eco_stage_id))
        return len(r)>0
    @api.model
    def approve(self):
        for record in self.filtered(lambda r:(not r.is_approved) and (not r.is_closed)  and (self.env.user.id in r.required_user_ids.mapped('id') or self.env.is_superuser()) and (r.template_stage_id==r.eco_stage_id)):
            record.user_id=self.env.user.id
            record.approval_date=fields.Date.today()
            record.status='approved'
        self.flush()
    @api.model            
    @api.returns('bool')
    def user_can_reject(self):
        r=self.filtered(lambda r:(not r.is_rejected) and (not r.is_closed)  and (self.env.user.id in r.required_user_ids.mapped('id') or self.env.is_superuser()) and (r.template_stage_id==r.eco_stage_id))
        return len(r)>0
    @api.model
    def reject(self):
        for record in self:
            record.user_id=self.env.user.id
            record.approval_date=fields.Date.today()
            record.status='rejected'

    @api.model
    @api.returns('bool')
    def need_approvals(self):
        return len(self.filtered(lambda r: not r.is_closed))>0

    @api.depends('status','required_user_ids')
    def _compute_status(self):
        for record in self:
            record.is_rejected=record.status=='rejected'
            record.is_approved=record.status=='approved'
            record.is_closed=record.is_rejected or record.is_approved or len(record.required_user_ids)==0

    @api.depends('user_ids')
    def _compute_required_users(self):
        for record in self:
            if record.approval_type=='mandatory':
                ids=record.user_ids.mapped('id')
                record.required_user_ids=[(6,0,ids)]