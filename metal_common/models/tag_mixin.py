# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class TagMixin(models.AbstractModel):
    _name='we.tag.mixin'
    _description='Tag  Mixin'
    # _inherit = ['model.mixin']
    name = fields.Char('Name', required=True, translate=True)