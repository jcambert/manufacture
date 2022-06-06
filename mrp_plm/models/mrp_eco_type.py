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
    stage_ids = fields.Many2one('mrp.plm.eco.stage', string='Stages')
    alias_id = fields.Many2one(
        'mail.alias', string='Alias', ondelete="restrict", required=True,
        help="The email address associated with this channel. New emails received will automatically create new leads assigned to the channel.")
    # alias: improve fields coming from _inherits, use inherited to avoid replacing them
    alias_user_id = fields.Many2one(
        'res.users', related='alias_id.alias_user_id', readonly=False, inherited=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('mrp_plm.group_mrp_plm_eco_user').id)])

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
            # res=self._eco.search_count([('state','not in',('done','rejected')),('type_id.id','=',record.id)])
            res=10
            record.nb_ecos = res

    def _compute_nb_validation(self):
        for record in self:
            record.nb_validation = 0

    def _alias_get_creation_values(self):
        values = super(EcoType, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('mrp.plm.eco.stage').id
        values['alias_name'] = False
        return values

    def write(self, vals):
        res = super(EcoType, self).write(vals)
        for type in self:
            alias_vals = type._alias_get_creation_values()
            type.write({
                    'alias_name': alias_vals.get('alias_name', type.alias_name),
                    'alias_defaults': alias_vals.get('alias_defaults'),
                })
        return res