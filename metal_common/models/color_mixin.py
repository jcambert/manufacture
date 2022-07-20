# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from random import randint
class ColorMixin(models.AbstractModel):
    _name='we.color.mixin'
    _description='Color Mixin'
    # _inherit = ['model.mixin']
    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color Index', default=_get_default_color)