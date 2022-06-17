# -*- coding: utf-8 -*-
from odoo import models, fields, api,_,tools
from odoo.exceptions import AccessError, UserError,ValidationError


class Material(models.Model):
    _name='metal.material'
    _description='Generic Material'
    _inherit=['metal.convention']
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"This name already exist !")
    ]

    @tools.ormcache()
    def _get_default_volmass_uom_categ(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('uom.uom_categ_volmass')

    name=fields.Char('Name',required=True)
    volmass=fields.Float('Volumic Mass',required=True,help="in m3/Kg")
    volmass_uom=fields.Many2one('uom.uom','Length Unit',required=True,domain="[('category_id','=',volmass_uom_categ)]")
    volmass_uom_categ=fields.Many2one('uom.category',default=_get_default_volmass_uom_categ,store=False,readonly=True)
    default=fields.Boolean('Default',default=False)

    @api.constrains('volmass')
    def _check_volmass(self):
        if any( record.volmass<=0 for record in self):
            raise ValidationError(_('The volumic mass must be greater than zero'))
    