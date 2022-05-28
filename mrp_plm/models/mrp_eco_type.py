# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EcoType(models.Model):
    _name = 'mrp.plm.eco.type'
    _description = 'Eco Type'
    _inherit = ['mail.thread', 'mail.alias.mixin', 'mail.activity.mixin','archive.mixin', 'sequence.mixin', 'company.mixin', 'color.mixin']
    _order = "sequence, name, id"
    _check_company_auto = True
    _sequence_name='mrp.plm.eco.type'
    name = fields.Char("Name", index=True, required=True, tracking=True)
    nb_approvals = fields.Integer('Nb Of Approvals', compute='_compute_nb_approval')
    nb_approvals_my = fields.Integer('My Nb Of Approvals', compute='_compute_nb_approval_my')
    nb_ecos = fields.Integer('Nb Of ECOs', compute='_compute_nb_eco')
    nb_validation = fields.Integer('Nb Of validation', compute='_compute_nb_validation')
    stage_ids = fields.Many2one('mrp.eco.stage', string='Stages')

    def _compute_nb_approval(self):
        for record in self:
            record.nb_approvals = 0

    def _compute_nb_approval_my(self):
        for record in self:
            # res=self._eco.search_count([('user_can_approve','=',True),('type_id.id','=',record.id)])
            res=10
            record.nb_approvals_my = res

    def _compute_nb_eco(self):
        for record in self:
            res=self._eco.search_count([('state','not in',('done','rejected')),('type_id.id','=',record.id)])
            record.nb_ecos = res

    def _compute_nb_validation(self):
        for record in self:
            record.nb_validation = 0

    def _alias_get_creation_values(self):
        values = super(EcoType, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('mrp.eco.stage').id
        
        return values