# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EcoApprovalTemplate(models.Model):
    _name='mrp.plm.eco.approval.template'
    _description='Eco Approval Template'
    _inherit=['we.sequence.mixin']
    _order="sequence,id"
    sequence = fields.Integer(string='Sequence',default=1,help="Ordering sequence")
    approval_type=fields.Selection([
        ('selection','Selection'),
        ('mandatory','Mandatory'),
        ('comment','Comment')],required=True,string="Validation Type")
    name=fields.Char('Role',required=True)
    stage_id=fields.Many2one('mrp.plm.eco.stage',ondelete='restrict',string="Stage")
    user_ids=fields.Many2many('res.users',ondelete='restrict',required=True)