# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
class ArchiveMixin(models.AbstractModel):
    _name='we.archive.mixin'
    _description='Archive Mixin'
    # _inherit = ['model.mixin']
    active = fields.Boolean('Active',default=True)

    @api.model
    def do_archive(self):
        for rec in self:
            rec.active = True