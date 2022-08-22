from odoo import api, exceptions, fields, models, _

# class QuotationMaterialVolumicMass(models.Model):
#     _name='metal.quotation.material.volumic.mass'
#     _description='Quotation Material Volumic Mass'
#     _inherit=[]
#     _order = "name"
#     _sql_constraints = [
#         ('name_uniq', 'unique (name)', "name already exists !"),
#     ]

#     name = fields.Char('Name',required=True,index=True)
#     density = fields.Float('Density',digits=(6,2),help="Density of the material in Kg/m3" )
#     material_ids = fields.One2many('metal.quotation.material','volumic_mass_id','Materials')

#     @api.constrains('density')
#     def _check_density(self):
#         if any( record.density<=0 for record in self):
#             raise exceptions.ValidationError(_('The density must be greater than zero'))


# volumic_mass_id=fields.Many2one('metal.quotation.material.volumic.mass','Volumic Mass',required=True)


class QuotationMaterialTemplate(models.Model):
    _name='metal.quotation.material.template'
    _description='Quotation Material Template'
    _inherit=['we.archive.mixin', 'we.sequence.mixin', 'we.company.currency.mixin','metal.quotation.template.mixin']
    _order = "name"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "name already exists !"),
    ]
    name = fields.Char('Name',required=True,index=True)
    # density=fields.Float('Density',digits=(6,2),help="Density of the material in Kg/m3" )
    density=fields.Float('Density',related='base_template_id.volmass',digits=(6,2),help="Density of the material in Kg/m3" )
    # volmass=fields.Float('Density',related='base_template_id.volmass',digits=(6,2),help="Density of the material in Kg/m3" )
    base_template_id=fields.Many2one('metal.material.template','Base Template',required=True)
    # performance: material_id provides prefetching on the first material only
    material_id = fields.Many2one('metal.quotation.material', 'Material', compute='_compute_material_id')
    material_ids = fields.One2many('metal.quotation.material','material_tmpl_id','Materials')
    price=fields.Monetary('Price',help="price per Kilogram", currency_field='currency_id')


    @api.depends('material_ids')
    def _compute_material_id(self):
        for p in self:
            p.material_id = p.material_ids[:1].id

    @api.model
    def copy_template_to_quotation(self,quotation_id):
        create=self.env['metal.quotation.material'].create
        datas=[]
        for record in self.filtered(lambda r:  not r.base):
            data={
                'quotation_id':quotation_id,
                'name':record.name,
                'material_tmpl_id':record.id,
                'price':record.price,
                }
            datas.append(data)
        create(datas)
    
    def add_template_to_quotation(self ,quotation_id,target_ids=False):
        if not target_ids:
            target_ids=self.env['metal.quotation.material.template'].search([]).mapped('id')
        current_in_quotation=self.env['metal.quotation.material'].search([('material_tmpl_id', 'in', target_ids)]).mapped('material_tmpl_id.id')
        self._add_template_to_quotation(self._name, target_ids,current_in_quotation,quotation_id)

# base_material_name = fields.Char('Template Name')
# base_material_density = fields.Float('Density',digits=(6,2),help="Density of the material in Kg/m3" )
class QuotationMaterial(models.Model):
    _name='metal.quotation.material'
    _description='Quotation Material'
    _inherit=['we.archive.mixin', 'we.sequence.mixin', 'we.company.currency.mixin','metal.quotation.template.inherit.mixin']
    _inherits = {'metal.quotation.material.template': 'material_tmpl_id'}
    _sql_constraints = [
        ('name_uniq', 'unique (name,quotation_id)', "name already exists in the quotation !"),
    ]
    material_tmpl_id = fields.Many2one('metal.quotation.material.template','Material Template',auto_join=True, index=True, ondelete="cascade", required=True)
    
    name=fields.Char('Name')
    
    price=fields.Monetary('Price',help="price per Kilogram", currency_field='currency_id')

   


    @api.onchange('material_tmpl_id')
    def on_material_tmpl_id_change(self):
        self.ensure_one()
        if self.material_tmpl_id:
            self.price = self.material_tmpl_id.price

    @api.model_create_multi
    def create(self, vals_list):
        
        materials = super(QuotationMaterial, self.with_context(create_metal_quotation_material=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants
        self.clear_caches()
        return materials

    def write(self, values):
        res = super(QuotationMaterial, self).write(values)
        if 'active' in values:
            # `_get_first_possible_variant_id` depends on variants active state
            self.clear_caches()
        return res