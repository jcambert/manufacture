from odoo import api, exceptions, fields, models, _

class AddTemplateToQuotationWizardMixin(models.TransientModel):
    _name='metal.quotation.template.wizard.mixin'
    _description='Template Wizard Mixin'

    #override this property to set the default quotation
    _template_name=''
    def get_default_quotation(self):
        quot= self.env.context.get('default_quotation_id',False)
        if not quot:
            quot=self.env['metal.quotation'].search([('state','=','draft')],limit=1)
        return quot
    quotation_id=fields.Many2one('metal.quotation',required=True,string='Quotation',default=get_default_quotation)

    def action_add_template(self):
        self.ensure_one()

    def add_template(self,target_ids):
    
        self.env[self._template_name].add_template_to_quotation(self.quotation_id.id,target_ids)

        return {
            'name': 'view_quotation_action',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.quotation',
            'res_id': self.quotation_id.id,
            'target': 'main',
            'context': {'default_quotation_id': self.quotation_id.id}
        }