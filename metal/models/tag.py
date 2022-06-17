# -*- coding: utf-8 -*-

from odoo import models, fields, api
class Tag(models.Model):
    _name='metal.tag'
    _description='Tag'
    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color Index')
    
    _sql_constraints = [
        ('tag_name_uniq', 'unique (name)', "Tag name already exists !"),
    ]