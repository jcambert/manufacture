# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class EcoBomChange(models.Model):
    _name = 'mrp.plm.eco.bom.change'
    _description='Modifications de la nomenclature OMT'

    change_type=fields.Selection([('add','Ajout'),('remove','Suppression'),('update','Mettre à jour')],string="Type de modification",required=True)
    conflict=fields.Boolean('Conflit',compute='_compute_conflict')
    eco_id=fields.Many2one('mrp.plm.eco',ondelete='restrict',string="ECO")
    eco_base_id=fields.Many2one('mrp.plm.eco',ondelete='restrict',string="ECO de base")
    new_operation_id=fields.Many2one('mrp.routing.workcenter',ondelete='restrict',string="Nouvelle opération")
    new_product_qty=fields.Float('Quantité')
    new_uom_id=fields.Many2one('uom.uom',string="Unité de mesure")
    old_operation_id=fields.Many2one('mrp.routing.workcenter',ondelete='restrict',string="Ancienne opération")
    old_product_qty=fields.Float('Quantité')
    old_uom_id=fields.Many2one('uom.uom',string="Unité de mesure")
    operation_change=fields.Char('Consommé dans l\'opération',compute='_compute_operation_change')
    product_id=fields.Many2one('product.product',ondelete='restrict',string="Produit")
    rebase_id=fields.Many2one('mrp.plm.eco',ondelete='restrict',string="Rebase")
    uom_change=fields.Char('Unité de mesure',compute='_compute_uom_change')
    upd_product_qty=fields.Float('Quantité',store=True,compute='_compute_upd_product_qty')

    @api.depends('change_type')
    def _compute_upd_product_qty(self):
        for record in self:
            if record.change_type=='update':
                record.upd_product_qty=record.new_product_qty
            else:
                record.upd_product_qty=record.old_product_qty
    @api.depends('old_uom_id','new_uom_id')
    def _compute_uom_change(self):
        for record in self:
            if record.old_uom_id and record.new_uom_id:
                record.uom_change=record.old_uom_id.name+' -> '+record.new_uom_id.name
            else:
                record.uom_change=''

    #@api.depends('new_operation_id','old_operation_id')
    def _compute_operation_change(self):
        for record in self:
            if record.new_operation_id and record.old_operation_id:
                record.operation_change='Opération modifiée'
            elif record.new_operation_id:
                record.operation_change='Opération ajoutée'
            elif record.old_operation_id:
                record.operation_change='Opération supprimée'
            else:
                record.operation_change=''

    #@api.depends('change_type','product_change','upd_product_qty','uom_change')
    def _compute_conflict(self):
        for record in self:
            record.conflict=False
            if record.change_type=='update':
                if record.product_change and record.upd_product_qty and record.uom_change:
                    record.conflict=True
            elif record.change_type=='add':
                if record.product_change and record.upd_product_qty and record.uom_change:
                    record.conflict=True
            elif record.change_type=='remove':
                if record.product_change and record.upd_product_qty and record.uom_change:
                    record.conflict=True
   # @api.constrains('change_type','product_change','upd_product_qty','uom_change')
    def check_conflict(self):
        for record in self:
            if record.conflict:
                raise ValidationError("Impossible de valider la modification car il y a un conflit")
    #@api.constrains('change_type','product_change','upd_product_qty','uom_change')
    def check_change_type(self):
        for record in self:
            if record.change_type=='update':
                if not record.product_change and not record.upd_product_qty and not record.uom_change:
                    raise ValidationError("Impossible de valider la modification")
            elif record.change_type=='add':
                if not record.product_change and not record.upd_product_qty and not record.uom_change:
                    raise ValidationError("Impossible de valider la modification")
            elif record.change_type=='remove':
                if not record.product_change and not record.upd_product_qty and not record.uom_change:
                    raise ValidationError("Impossible de valider la modification")
    @api.constrains('new_operation_id','old_operation_id')
    def check_operation_id(self):
        for record in self:
            if record.new_operation_id and record.old_operation_id:
                if record.new_operation_id.id==record.old_operation_id.id:
                    raise ValidationError("La nouvelle opération et l'ancienne opération sont identiques")
    @api.constrains('new_product_qty','old_product_qty')
    def check_product_qty(self):
        for record in self:
            pass

    @api.model
    def product_change(self):
        for record in self:
            if record.product_id:
                record.product_change=True
            else:
                record.product_change=False