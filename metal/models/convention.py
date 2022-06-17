# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError
import re

class Convention(models.Model):
    _name='metal.convention'
    _description='Convention RegEx searching'
    convention=fields.Char('Convention',help="python regex string convention")
    @api.onchange('convention')
    def on_convention_changed(self):
        if isinstance(self.convention,str):
            self.convention = str(self.convention).strip()
        return
    @api.model
    def parse(self,convention,value,results):
        p = re.compile(convention,re.IGNORECASE)
        m = p.match(value)
        if m:
            if isinstance(results,dict):
                results.update(m.groupdict())
            return True
        return False