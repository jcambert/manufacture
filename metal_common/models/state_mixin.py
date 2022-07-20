# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class StateMixin(models.AbstractModel):
    _name='we.state.mixin'
    _description='State Mixin'
    # _inherit = ['model.mixin']
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done','Done'),
        ('locked', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')