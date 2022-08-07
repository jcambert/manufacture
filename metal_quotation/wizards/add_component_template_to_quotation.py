from odoo import api, exceptions, fields, models, _

class AddComponentTemplateWizardMixin(models.TransientModel):
    _name='metal.quotation.component.add.component.template.mixin'
    _description='Add Component Template to Quotation'
    _inherit=['metal.quotation.template.wizard.mixin']
    _template_name='metal.quotation.component.template'
    

class AddComponentTemplateToQuotationWizard(models.TransientModel):
    _name='metal.add.component.template.to.quotation.wizard'
    _description='Add Component Template To Quotation Wizard'
    _inherit=['metal.quotation.component.add.component.template.mixin']
    
    component_tmpl_id=fields.Many2one('metal.quotation.component.template',required=True,string='Component Template',default=lambda self: self.env.context.get('default_component_tmpl_id',False))
 
    def action_add_template(self):
        self.ensure_one()
        component_ids=[self.component_tmpl_id.id]
        return self.add_template(component_ids)


class AddComponentsTemplatesToQuotationWizard(models.TransientModel):
    _name='metal.add.components.templates.quotation.wizard'
    _description='Add Components Templates To Quotation Wizard'
    _inherit=['metal.quotation.component.add.component.template.mixin']

    def get_default_component_tmpl_ids(self):
        component_tmpl_ids=self.env.context.get('default_component_tmpl_ids',False)
        if not component_tmpl_ids:
            component_tmpl_ids=self.env[self._template_name].search([]).mapped('id')
        return component_tmpl_ids
    
    def action_add_template(self):
        self.ensure_one()

        component_ids=self.get_default_component_tmpl_ids()

        return self.add_template(component_ids)
