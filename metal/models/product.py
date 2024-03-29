# -*- coding: utf-8 -*-
from odoo import models, fields, api,_,tools
from odoo.exceptions import AccessError, UserError,ValidationError
from .settings import SHEETMETAL_CATEGORY
from ast import literal_eval
import logging
import re
import math
import sys
_logger = logging.getLogger(__name__)
ALLOWED_EVAL_NAMES = {
    k: v for k, v in math.__dict__.items() if not k.startswith("__")
}
ALLOWED_EVAL_FIELDS=['length','width','height','thickness','volmass']
def eval_expression(input_string,allowed_fields,**kwargs):
     # Step 1
     allowed_names = ALLOWED_EVAL_NAMES
     # Step 2
     code = compile(input_string, "<string>", "eval")
     # Step 3
     for name in code.co_names:
         if name not in allowed_names and name not in allowed_fields:
             # Step 4
             raise NameError(f"Use of {name} not allowed")
     return eval(code, {"__builtins__": {}}, kwargs)
def compute_formula_value(w_formula,**kwargs):
    result=0
    try:
        result=eval_expression(w_formula,ALLOWED_EVAL_FIELDS,**kwargs)

    except :
        _logger.warning('an error occur while calculating value\n',sys.exc_info()[0])
        print(kwargs)
        print(w_formula)
    finally:
        return result
def compute_standard_weight(length,weight_per_length):
    return length*weight_per_length
def compute_profile_calculated_weight():
    pass    
class ProductTemplate(models.Model):
    _inherit = ['product.template']
    _description = 'Product Metal Template'
    _sql_constraints = [
        ('metal_product_name_uniq','unique(name)',"This name already exist !")
    ]

    state = fields.Selection(
        [('draft','Draft'),('running','running'),('closed','Closed')],
        string='State',
        default='draft',
        copy=False,required=True,help="Statut",tracking=True,store=True)
    material = fields.Many2one('metal.material','Material')
    finition = fields.Char('Finition',default='')

    cattype=fields.Selection(related='categ_id.cattype',string='Category Type')
    protype=fields.Selection(related='categ_id.protype',string='Profile Type')

    weight_per_length=fields.Float('Weight per Unit Length') #if profile
    surface_per_length=fields.Float('Surface per Unit Length') #if profile
    surface_section=fields.Float('Surface section') #if profile

    surface=fields.Float('Surface', digits='Product Unit of Measure',default=0.0)

    linear_weight=fields.Float('Linear weight',compute='_compute_linear_weight',help='Weight per base unit length')
    length=fields.Float('Length',digits='Product Unit of Measure',default=0.0,help="Length for sheetmetal or profile or pipe")
    width=fields.Float('Width',digits='Product Unit of Measure',default=0.0,help="Width for sheetmetal or rect/square pipe ")#Width | external diameter
    height=fields.Float('Height',digits='Product Unit of Measure',default=0.0,help="Height for rect/square pipe or External diameter")#length | external diameter
    # dim3=fields.Float('dim3',digits='Product Unit of Measure',default=0.0)#Length, internal diameter
    # dim4=fields.Float('dim4',digits='Product Unit of Measure',default=0.0)#Width, internal diameter
    thickness=fields.Float('Thickness',digits='Product Unit of Measure',default=0.0,help="Thickness for Sheetmetal and Pipe")#thickness

    length_uom=fields.Many2one(related="categ_id.length_uom")
    surface_uom=fields.Many2one(related="categ_id.surface_uom")
    weight_uom=fields.Many2one(related="categ_id.weight_uom")

    is_sheetmetal=fields.Boolean('Is Sheetmetal product',compute='_compute_is_sheetmetal')
    is_profile=fields.Boolean('Is Profile product',compute='_compute_is_sheetmetal')

    @api.depends('categ_id')
    def _compute_is_sheetmetal(self):
        for record in self:
            record.is_sheetmetal=self.categ_id.cattype in ['sheetmetal']
            record.is_profile=self.categ_id.cattype in ['profile']

    @api.onchange('name')
    def set_upper(self):    
        if isinstance(self.name,str):
            force=self.env['ir.config_parameter'].get_param('metal.product_name_force_uppercase')
            self.name = str(self.name).upper() if force else str(self.name)
        return


  

    def _filterByRe(self,*args):
        if len(args) not in [2,3]:
            return False
        convention,name,res=args[0],args[1],args[2] if len(args)==3 else None
        if(not convention or not name or len(convention)==0 or len(name)==0):
            return False
        _logger.info(f"Filtering: Convention->{convention} , name->{name}")
        p = re.compile(convention,re.IGNORECASE)
        m = p.match(name)
        if m:
            if isinstance(res,dict):
                res.update(m.groupdict())
            return True
        return False
    

    
    

    def parse(self,convention,value,results):
        p = re.compile(convention,re.IGNORECASE)
        m = p.match(value)
        if m:
            if isinstance(results,dict):
                results.update(m.groupdict())
            return True
        return False
    @api.onchange('categ_id','name')
    def _compute_type(self):
        try:
            record=self
            if not record.categ_id or not record.name:
                return
            if not categ.convention or not self.parse(categ.convention,record.name,groups):
                return
            materials=self.env['metal.material'].search([])
            groups={}
            categ=record.categ_id
            
            if 'material' in groups:
                material=materials.filtered(lambda r:self._filterByRe(r.convention,groups['material']))
                if material.exists() :
                    self.material=material[0]
            else:
                material=materials.filtered(lambda r:r.default)
                if material.exists()    :
                    self.material=material[0]
                
                uom=self.categ_id.length_uom

            if 'format' in groups and not record.is_product_variant:
                format=self.env['product.attribute.value'].search([('code_suffixe','ilike',groups['format'])],limit=1)
                if format:
                    self.length=format.length
                    self.width=format.width

            else:
                if 'length' in groups:
                    self.length=float(groups['length'])
                if 'width' in groups:
                    self.width=float(groups['width'])
            if 'height' in groups:
                self.height=float(groups['height'])
            if 'thickness' in groups:
                self.thickness=float(groups['thickness'])
            if 'finition' in groups:
                self.finition=groups['finition']
            if 'value' in groups and 'name' in groups:
                value=int(groups['value'])
                name=groups['name']
                if categ.cattype=='profile' and categ.protype=='standard':
                    profile=self.env['metal.profile'].search([('protype.name','=',name), ('name','=',value)])
                    if profile.exists():
                        profile=profile[0]
                        self.weight_per_length=profile.weight_per_length
                        self.surface_per_length=profile.surface_per_length
                        self.surface_section=profile.surface_section
        except Exception as e:
            _logger.error(e)
            pass
    
    @api.onchange('weight')            
    def _compute_linear_weight(self):
        for record in self:
            #TODO Compute weight per meter usin uom
            record.linear_weight=0.0

    def calculate_weight(self):
        self.ensure_one()
        record=self
        
        if not record.is_product_variant:
            # length,width,height,thickness,volmass=record.length,record.width,record.height,record.thickness,record.material.volmass
            # s_formula,w_formula=record.categ_id.surface_formula,record.categ_id.weight_formula
            # s_code, w_code=compile(s_formula, "<string>", "eval"),compile(w_formula, "<string>", "eval")
            # record.surface, record.weight=float(eval(s_code)),float(eval(w_code))
            if record.cattype=='sheetmetal':
                record.weight= compute_formula_value(record.categ_id.weight_formula,length=record.length,width=record.width,thickness=record.thickness,volmass=record.material.volmass)
                record.surface= compute_formula_value(record.categ_id.surface_formula,length=record.length,width=record.width)
            elif record.cattype=='profile' and record.protype=='calculated':
                record.weight=compute_formula_value(record.categ_id.weight_formula,length=record.length,width=record.width,height=record.height,thickness=record.thickness,volmass=record.material.volmass)
            elif record.cattype=='profile' and record.protype=='standard':
                record.weight=compute_standard_weight( record.length,record.weight_per_length)
        

    @api.onchange('length','width','height','thickness','material')
    def compute_weight(self):
        for record in self:
            record.calculate_weight()
    def action_update_weight(self):
        self.ensure_one()
        if self.product_variant_count>1:
            variants=self.env['product.product'].search([('product_tmpl_id.id','=',self.id)])
            for variant in variants:
                variant._update_data()
        else:
            self.calculate_weight()
    # @api.constrains('dim2')
    def _check_sheetmetal_width(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.dim2<=0:
                raise ValidationError(_('Sheetmetal width must be greater than 0'))

    # @api.constrains('dim1')
    def _check_sheetmetal_length(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.dim1<=0:
                raise ValidationError(_('Sheetmetal length must be greater than 0'))
            
    # @api.constrains('dim5')
    def _check_sheetmetal_thickness(self):
        if any( record.is_sheetmetal and record.dim5<=0 for record in self):
            raise ValidationError(_('Sheetmetal thickness must be greater than 0'))
        #thickness profile can be 0 

    
            


    # def action_view_indice(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("weMetalProduct.we_indice_action")
    #     action['domain'] = [ ('product', 'in', self.ids)]
    #     action['context'] = {}
    #     return action

class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Product Metal'
    # product_type=fields.Selection(related='product_tmpl_id.product_type',string='Type',store=False)
    length=fields.Float(compute='_compute_size',store=True)
    width=fields.Float(compute='_compute_size',store=True)
    height=fields.Float(compute='_compute_size',store=True)
    thickness=fields.Float(related='product_tmpl_id.thickness',string='Thickness',store=True)
    material= fields.Many2one('metal.material',related='product_tmpl_id.material')
    surface=fields.Float('Surface', digits='Product Unit of Measure',default=0.0)
    weight_per_length=fields.Float('Weight per Unit Length')
    protype=fields.Selection(related="product_tmpl_id.protype")
    def _update_data(self):
        self.ensure_one()
        product=self
        if product.product_tmpl_id.cattype=='sheetmetal' and product.product_template_attribute_value_ids.attribute_id.display_type=='sheetmetalsize':
            product.default_code=product.product_tmpl_id.name + product.product_template_attribute_value_ids.product_attribute_value_id.code_suffixe
            
            length=product.product_template_attribute_value_ids.product_attribute_value_id.length
            product.length=product.product_template_attribute_value_ids.attribute_id.uom_id._compute_quantity(length,product.length_uom)
            
            width=product.product_template_attribute_value_ids.product_attribute_value_id.width
            product.width=product.product_template_attribute_value_ids.attribute_id.uom_id._compute_quantity(width,product.length_uom)

            # length,width,thickness,volmass=product.length,product.width,product.thickness,product.material.volmass
            # s_formula, v_formula, w_formula=product.categ_id.surface_formula,product.categ_id.volume_formula,product.categ_id.weight_formula
            # s_code=compile(s_formula, "<string>", "eval")
            # v_code=compile(v_formula, "<string>", "eval")
            # w_code=compile(w_formula, "<string>", "eval")
            # product.surface,product.volume, product.weight=float(eval(s_code)),float(eval(v_code)),float(eval(w_code))
            # product.surface,product.volume=float(eval(s_code)),float(eval(v_code))
            product.weight=compute_formula_value(product.categ_id.weight_formula,length=product.length,width=product.width,thickness=product.thickness,volmass=product.material.volmass)
        elif product.product_tmpl_id.cattype=='profile' and product.product_tmpl_id.protype=='calculated' and product.product_template_attribute_value_ids.attribute_id.display_type=='profilelength':
            product.default_code=product.product_tmpl_id.name + product.product_template_attribute_value_ids.product_attribute_value_id.code_suffixe
            
            length=product.product_template_attribute_value_ids.product_attribute_value_id.length
            product.length=product.product_template_attribute_value_ids.attribute_id.uom_id._compute_quantity(length,product.length_uom)
            
            product.width=product.product_tmpl_id.width
            product.height=product.product_tmpl_id.height
            # length,width,height,thickness,volmass=product.length,product.width,product.height,product.thickness,product.material.volmass
            w_formula=product.categ_id.weight_formula
            # if w_formula and len(w_formula)>0:
            #     w_code=compile(w_formula, "<string>", "eval")
            #     product.weight=float(eval(w_code))
            product.weight=compute_formula_value(w_formula,length=product.length, width=product.width,height=product.height,thickness=product.thickness,volmass=product.material.volmass)
        elif product.product_tmpl_id.cattype=='profile' and product.product_tmpl_id.protype=='standard' and product.product_template_attribute_value_ids.attribute_id.display_type=='profilelength':
            product.default_code=product.product_tmpl_id.name + product.product_template_attribute_value_ids.product_attribute_value_id.code_suffixe
            
            length=product.product_template_attribute_value_ids.product_attribute_value_id.length
            product.length=product.product_template_attribute_value_ids.attribute_id.uom_id._compute_quantity(length,product.length_uom)
            
            product.weight_per_length=product.product_tmpl_id.weight_per_length
            product.weight=compute_standard_weight(product.length,product.weight_per_length)
        else:
            product.length=0.0
    @api.depends('product_template_attribute_value_ids','product_tmpl_id.name','product_tmpl_id.categ_id')
    def _compute_size(self):
        for product in self:
            # indices = product.product_template_attribute_value_ids._ids2str()
            # print(product.product_template_attribute_value_ids.attribute_id)
            # print(product.product_template_attribute_value_ids.product_attribute_value_id)

            #  if record.cattype=='sheetmetal':
            # elif record.cattype=='profile' and record.protype=='calculated':
            # elif record.cattype=='profile' and record.protype=='standard':
            product._update_data()
    def action_update_weight(self):
        self.ensure_one()
        self._update_data()