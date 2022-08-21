# -*- coding: utf-8 -*-
from odoo import models, fields, api,_,tools
from odoo.exceptions import AccessError, UserError,ValidationError

class MaterialTemplate(models.Model):
    _name='metal.material.template'
    _description='Material Template'
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"This name already exist !")
    ]
    @tools.ormcache()
    def _get_default_volmass_uom_categ(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('metal.uom_categ_volmass')
    @api.constrains('volmass')
    def _check_volmass(self):
        if any( record.volmass<=0 for record in self):
            raise ValidationError(_('The volumic mass must be greater than zero'))

    name=fields.Char('Name',required=True)
    volmass=fields.Float('Volumic Mass',required=True,help="Volumic mass of the material")
    volmass_uom=fields.Many2one('uom.uom','Volumic Mass UOM',required=True,domain="[('category_id','=',volmass_uom_categ)]")
    volmass_uom_categ=fields.Many2one('uom.category', default=_get_default_volmass_uom_categ,store=False,readonly=True)
    material_ids=fields.One2many('metal.material','material_tmpl_id','Materials')

class Material(models.Model):
    _name='metal.material'
    _description='Generic Material'
    _inherit=['metal.convention']
    _inherits = {'metal.material.template': 'material_tmpl_id'}
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"This name already exist !")
    ]
    name=fields.Char('Name',required=True)
    material_tmpl_id=fields.Many2one('metal.material.template','Material Template',required=True,ondelete='cascade')
    default=fields.Boolean('Default',default=False)
    normative_body=fields.Many2one('metal.normative.body','Normative Body',required=False)
    # equivalent=fields.Many2many('metal.material','metal_material_equivalent_rel','material_id','equivalent_id','Equivalent')
    
class NormativeBody(models.Model):
    _name='metal.normative.body'
    _description='Organisme Normatif (AISI,NF,UNI, DIN)'
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"This name already exist !")
    ]
    _inherit=['we.tag.mixin']
    description=fields.Text('Description')
    material_ids=fields.One2many('metal.material','normative_body','Materials')

 