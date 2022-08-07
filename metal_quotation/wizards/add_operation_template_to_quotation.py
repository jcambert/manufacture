from odoo import api, exceptions, fields, models, _

class AddOperationTemplateWizardMixin(models.TransientModel):
    _name='metal.quotation.operation.add.operation.template.mixin'
    _description='Add Operation Template to Quotation'
    _inherit=['metal.quotation.template.wizard.mixin']
    _template_name='metal.quotation.operation.template'

class AddOperationTemplateToQuotationWizard(models.TransientModel):
    _name='metal.add.operation.template.to.quotation.wizard'
    _description='Add Operation To Quotation Wizard'
    _inherit=['metal.quotation.operation.add.operation.template.mixin']
    # name = fields.Char('Name',required=True,index=True)
    # help = fields.Text('Help')
    # workcenter_id = fields.Many2one('mrp.workcenter',string='Workcenter')
    
    operation_tmpl_id=fields.Many2one('metal.quotation.operation.template',required=True,string='Operation Template',default=lambda self: self.env.context.get('default_operation_tmpl_id',False))
    # operation_cost = fields.Integer('Operation Cost')
    # operation_base_time = fields.Float('Operation Time')
    # preparation_cost = fields.Integer('Preparation Cost')
    # preparation_time = fields.Integer('Preparation Time')
    # quotation_id = fields.Many2one('metal.quotation',string='Quotation',required=True,default=lambda self: self.env.context.get('default_quotation_id',False))

    def action_add_template(self):
        self.ensure_one()
        operation_ids=[self.operation_tmpl_id.id]
        return self.add_template(operation_ids)

class AddOperationsTemplatesToQuotationWizard(models.TransientModel):
    _name='metal.add.operations.templates.quotation.wizard'
    _description='Add Operations Templates To Quotation Wizard'
    _inherit=['metal.quotation.operation.add.operation.template.mixin']

    def get_default_operation_tmpl_ids(self):
        tmpl_ids=self.env.context.get('default_operation_tmpl_ids',False)
        if not tmpl_ids:
            tmpl_ids=self.env[self._template_name].search([]).mapped('id')
        return tmpl_ids
    
    def action_add_template(self):
        self.ensure_one()

        operation_ids=self.get_default_operation_tmpl_ids()

        return self.add_template(operation_ids)