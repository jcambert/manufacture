# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class PriorityMixin(models.AbstractModel):
    _name='we.priority.mixin'
    _description='Priority Mixin'
    # _inherit = ['model.mixin']
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True, string="Priority")