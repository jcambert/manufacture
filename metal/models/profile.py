# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError
class ProfileType(models.Model):
    _name='metal.profile.type'
    _description='Standard Profile Type' #UPN HEA ..
    _order='name'
    _sql_constraints = [
        ('metal_profil_type_name_uniq','unique(name)',"The name of this profile type must be unique"),
    ]
    name=fields.Char('Name',required=True)

class Profile(models.Model):
    _name='metal.profile'
    _description='Standard Profile Dimension'
    _sql_constraints = [
        ('metal_profile_name_uniq','unique(protype,name)',"The name of this profile type must be unique"),
    ]
    name=fields.Char('Name',required=True,index=True)
    protype=fields.Many2one('metal.profile.type',required=True,string="Type")
    weight_per_length=fields.Float('Weight per Unit Length')
    surface_per_length=fields.Float('Surface per Unit Length')
    surface_section=fields.Float('Surface section')

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'protype'])
        return [(record.id, '%s-%s' % (record.protype.name , record.name))
                for record in self]