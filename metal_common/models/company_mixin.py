# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class CompanyMixin(models.AbstractModel):
    _name='we.company.mixin'
    _description='Company Mixin'
    # _inherit = ['model.mixin']
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

class CompanyCurrencyMixin(models.AbstractModel):
    _name='we.company.currency.mixin'
    _description='Company Mixin'
    _inherit=['we.company.mixin']
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True,store=True)