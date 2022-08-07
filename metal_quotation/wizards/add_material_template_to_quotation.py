from odoo import api, exceptions, fields, models, _

class AddMaterialTemplateWizardMixin(models.TransientModel):
    _name='metal.quotation.material.add.material.template.mixin'
    _description='Add Material Template to Quotation'
    _inherit=['metal.quotation.template.wizard.mixin']
    _template_name='metal.quotation.material.template'
    # def get_default_quotation(self):
    #     quot= self.env.context.get('default_quotation_id',False)
    #     if not quot:
    #         quot=self.env['metal.quotation'].search([('state','=','draft')],limit=1)
    #     return quot
    # quotation_id=fields.Many2one('metal.quotation',required=True,string='Quotation',default=get_default_quotation)

    # def action_add_template(self):
    #     self.ensure_one()

    # def add_template(self,material_ids):
    
    #     self.env['metal.quotation.material.template'].add_template_to_quotation(material_ids,self.quotation_id.id)

    #     return {
    #         'name': 'view_quotation_action',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'metal.quotation',
    #         'res_id': self.quotation_id.id,
    #         'target': 'main',
    #         'context': {'default_quotation_id': self.quotation_id.id}
    #     }

class AddMaterialTemplateToQuotationWizard(models.TransientModel):
    _name='metal.add.material.template.to.quotation.wizard'
    _description='Add Material Template To Quotation Wizard'
    _inherit=['metal.quotation.material.add.material.template.mixin']
    
    material_tmpl_id=fields.Many2one('metal.quotation.material.template',required=True,string='Material Template',default=lambda self: self.env.context.get('default_material_tmpl_id',False))
 
    def action_add_template(self):
        self.ensure_one()
        material_ids=[self.material_tmpl_id.id]
        return self.add_template(material_ids)


class AddMaterialsTemplatesToQuotationWizard(models.TransientModel):
    _name='metal.add.materials.templates.quotation.wizard'
    _description='Add Materials Templates To Quotation Wizard'
    _inherit=['metal.quotation.material.add.material.template.mixin']

    def get_default_material_tmpl_ids(self):
        material_tmpl_ids=self.env.context.get('default_material_tmpl_ids',False)
        if not material_tmpl_ids:
            material_tmpl_ids=self.env[self._template_name].search([]).mapped('id')
        return material_tmpl_ids
    
    def action_add_template(self):
        self.ensure_one()

        material_ids=self.get_default_material_tmpl_ids()

        return self.add_template(material_ids)
