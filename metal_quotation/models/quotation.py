from odoo import api, exceptions, fields, models, _
from . import common



class QuotationTemplate(models.Model):
    _name = 'metal.quotation.template'
    _description = 'Quotation Template'
    _order = "sequence, id"
    _inherit=['sequence.mixin','archive.mixin','company.currency.mixin','color.mixin','mail.thread', 'mail.activity.mixin', 'image.mixin','state.mixin']
    _check_company_auto = True

    date_order = fields.Datetime(string='Quotation Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent quotation")
    description = fields.Char('Description',states={'locked':[('readonly',True)],'cancel':[('readonly',True)]})
    is_quotation_variant = fields.Boolean(compute='_compute_is_quotation_variant')
    quotation_variant_ids = fields.One2many('metal.quotation', 'quotation_tmpl_id', 'Quotations', required=True)
    quotation_variant_count = fields.Integer('# Quotations Variants', compute='_compute_quotation_variant_count')
    material_margin = fields.Integer( string="Material Margin")
    component_margin = fields.Integer( string="Component Margin")
    be_time = fields.Integer( string="Default Etude Time")
    be_cost = fields.Monetary( string="Default Be Cost")
    fad_cost = fields.Monetary( string="Default FAD Cost")
    tool_cost = fields.Monetary( string="Default Tool Cost")
    st_margin = fields.Integer( string="Default ST Margin")

    def _compute_is_quotation_variant(self):
        self.is_quotation_variant = False

    @api.depends('quotation_variant_ids.quotation_tmpl_id')
    def _compute_quotation_variant_count(self):
        for template in self:
            template.quotation_variant_count = len(template.quotation_variant_ids)
            
class Quotation(models.Model):
    _name = 'metal.quotation'
    _description = 'Quotation'
    _order = "sequence, id"
    _inherits = {'metal.quotation.template': 'quotation_tmpl_id'}
    _inherit=['sequence.mixin','archive.mixin','company.currency.mixin','color.mixin','mail.thread', 'mail.activity.mixin', 'image.mixin','state.mixin']
    
    quotation_tmpl_id = fields.Many2one('metal.quotation.template', 'Quotation Template',auto_join=True, index=True, ondelete="cascade", required=True)
    is_quotation_variant = fields.Boolean(compute='_compute_is_quotation_variant')

    date_order = fields.Datetime(string='Quotation Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent quotation")
    description = fields.Char('Description',states={'locked':[('readonly',True)],'cancel':[('readonly',True)]})
    material_margin = fields.Integer( string="Material Margin")
    component_margin = fields.Integer( string="Component Margin")
    be_time = fields.Integer( string="Default Etude Time")
    be_cost = fields.Monetary( string="Default Be Cost")
    fad_cost = fields.Monetary( string="Default FAD Cost")
    tool_cost = fields.Monetary( string="Default Tool Cost")
    st_margin = fields.Integer( string="Default ST Margin")

    def _compute_is_quotation_variant(self):
        self.is_quotation_variant = True