from odoo import api, exceptions, fields, models, _

class QuotationComponentTemplate(models.Model):
    _name='metal.quotation.component.template'
    _description='Quotation Component Template'
    _inherit=['we.archive.mixin', 'we.sequence.mixin','metal.quotation.template.mixin']
    _order='sequence'
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "name already exists !"),
    ]
    name = fields.Char('Name',required=True,index=True)
    description = fields.Text('Description')
    unit_cost=fields.Float('Unit Cost',digits=(6,2))
    
    @api.model
    def copy_template_to_quotation(self,quotation_id):
        create=self.env['metal.quotation.component'].create
        datas=[]
        for record in self.filtered(lambda r:  not r.base):
            data={
                
                'quotation_id':quotation_id,
                'name':record.name,
                'component_tmpl_id':record.id,
                'name':record.name,
                'description':record.description,
                'unit_cost':record.unit_cost,
                }
            datas.append(data)
        create(datas)
    
    def add_template_to_quotation(self,quotation_id,target_ids=False ):
        if not target_ids:
            target_ids=self.env['metal.quotation.component.template'].search([]).mapped('id')
        current_in_quotation=self.env['metal.quotation.component'].search([('component_tmpl_id', 'in', target_ids)]).mapped('component_tmpl_id.id')
        self._add_template_to_quotation(self._name, target_ids,current_in_quotation,quotation_id)

class QuotationComponent(models.Model):
    _name='metal.quotation.component'
    _description='Quotation Component'
    _inherit=['metal.quotation.template.mixin']
    _inherit=['we.archive.mixin', 'we.sequence.mixin','metal.quotation.template.inherit.mixin']
    _inherits={'metal.quotation.component.template':'component_tmpl_id'}

    name = fields.Char('Name',required=True,index=True)
    description = fields.Text('Description')
    unit_cost=fields.Float('Unit Cost',digits=(6,2))
    
    component_tmpl_id=fields.Many2one('metal.quotation.component.template',string='Quotation Component Template',required=True,ondelete='cascade',default=lambda self: self.env.context.get('default_component_tmpl_id',False))

    @api.model_create_multi
    def create(self, vals_list):
        # if not 'component_tmpl_id' in vals_list:
        #     raise exceptions.UserError(_('You cannot create a component without a component template.'))
        operations = super(QuotationComponent, self.with_context(create_metal_quotation_component=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants
        self.clear_caches()
        return operations
    @api.model
    def default_get(self, fields_list):
        values = super(QuotationComponent, self).default_get(fields_list)
        if not 'component_tmpl_id' in values or not values['component_tmpl_id']:
            component_tmpl_id=self.env['metal.quotation.component.template'].search([('base','=',True)],limit=1).mapped('id')[0]
            if not component_tmpl_id :
                raise exceptions.UserError(_('You cannot create a component without a component template based.'))
            values['component_tmpl_id']=component_tmpl_id
        return values

    def write(self, values):
        res = super(QuotationComponent, self).write(values)
        if 'active' in values:
            # `_get_first_possible_variant_id` depends on variants active state
            self.clear_caches()
        return res