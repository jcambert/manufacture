# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EcoTag(models.Model):
    _name = 'mrp.plm.eco.tag'
    _description = 'Eco Tag'
    _inherit = ['color.mixin']

    name = fields.Char('Name', required=True, translate=True)
    