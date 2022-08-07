from odoo import api, exceptions, fields, models, _
class QuotationOperationTemplate(models.Model):
    _name='metal.quotation.operation.template'
    _description='Quotation Operation Template'
    _inherit=['we.archive.mixin', 'we.sequence.mixin','metal.quotation.template.mixin']
    _order='sequence'
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "name already exists !"),
    ]
    name = fields.Char('Name',required=True,index=True)
    help = fields.Text('Help')
    workcenter_id = fields.Many2one('mrp.workcenter',string='Workcenter',required=True)

    operation_ids=fields.One2many('metal.quotation.operation','operation_tmpl_id',string='Operations')
    
    operation_cost = fields.Integer('Operation Cost')
    operation_base_time = fields.Float('Operation Time',digits=(5,4))
    preparation_cost = fields.Integer('Preparation Cost')
    preparation_time = fields.Float('Preparation Time',digits=(6,4))

    @api.model
    def copy_template_to_quotation(self,quotation_id):
        create=self.env['metal.quotation.operation'].create
        datas=[]
        for record in self.filtered(lambda r:  not r.base):
            data={
                
                'quotation_id':quotation_id,
                'name':record.name,
                'operation_tmpl_id':record.id,
                'name':record.name,
                'help':record.help,
                'operation_cost':record.operation_cost,
                'operation_base_time':record.operation_base_time,
                'preparation_cost':record.preparation_cost,
                'preparation_time':record.preparation_time,
                }
            datas.append(data)
        create(datas)
    
    def add_template_to_quotation(self,quotation_id,target_ids=False ):
        if not target_ids:
            target_ids=self.env['metal.quotation.operation.template'].search([]).mapped('id')
        current_in_quotation=self.env['metal.quotation.operation'].search([('operation_tmpl_id', 'in', target_ids)]).mapped('operation_tmpl_id.id')
        self._add_template_to_quotation(self._name, target_ids,current_in_quotation,quotation_id)

class QuotationOperation(models.Model):
    _name='metal.quotation.operation'
    _description='Quotation Operation'
    _inherit=['we.archive.mixin', 'we.sequence.mixin','metal.quotation.template.inherit.mixin']
    _inherits={'metal.quotation.operation.template':'operation_tmpl_id'}
    _sql_constraints = [
        ('name_uniq', 'unique (name,quotation_id)', "name already exists in the quotation !"),
    ]

    operation_tmpl_id=fields.Many2one('metal.quotation.operation.template',string='Quotation Operation Template',auto_join=True, index=True, ondelete="cascade", required=True)

    name = fields.Char('Name',required=True,index=True)
    help = fields.Text('Help')
   
    operation_cost = fields.Integer('Operation Cost')
    operation_base_time = fields.Float('Operation Time',digits=(5,4))
    preparation_cost = fields.Integer('Preparation Cost')
    preparation_time = fields.Float('Preparation Time',digits=(6,4))

    @api.model_create_multi
    def create(self, vals_list):
        
        operations = super(QuotationOperation, self.with_context(create_metal_quotation_material=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants
        self.clear_caches()
        return operations

    def write(self, values):
        res = super(QuotationOperation, self).write(values)
        if 'active' in values:
            # `_get_first_possible_variant_id` depends on variants active state
            self.clear_caches()
        return res