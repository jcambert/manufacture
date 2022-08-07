from odoo import api, exceptions, fields, models, _


class QuotationMixin(models.AbstractModel):
    _name = 'metal.quotation.mixin'
    _description = 'Quotation Mixin'
    _inherit=['we.company.currency.mixin']
    material_margin = fields.Integer( string="Material Margin")
    component_margin = fields.Integer( string="Component Margin")
    be_time = fields.Integer( string="Default Etude Time")
    be_cost = fields.Monetary( string="Default Be Cost")
    fad_cost = fields.Monetary( string="Default FAD Cost")
    tool_cost = fields.Monetary( string="Default Tool Cost")
    st_margin = fields.Integer( string="Default ST Margin")
    note=fields.Text(string='Note')

     # name = fields.Char(string='Name', required=True,index=True)
    # description = fields.Char('Description')
    # revision=fields.Char(string='Revision')
    # quotation_id=fields.Many2one('metal.quotation',ondelete='cascade',string='Quotation')
    # quotation_product_ids = fields.One2many('metal.quotation.product', 'quotation_id', string='Quotation Products')
    # quotation_product_count = fields.Integer(string='Quotation Products Count', compute='_compute_quotation_product_count')

    # @api.depends('quotation_product_ids')
    # def _compute_quotation_product_count(self):
    #     for record in self:
    #         record.quotation_product_count = len(record.quotation_product_ids)

    # @api.multi
    # def action_view_quotation_product(self):
    #     action = self.env.ref('we_manufacture.action_metal_quotation_product').read()[0]
    #     action['domain'] = [('quotation_id', '=', self.id)]
    #     return action

    # @api.multi
    # def action_view_quotation_product_form(self):
    #     action = self.env.ref('we_manufacture.action_metal_quotation_product_form').read()[0]
    #     action['context'] = {'default_quotation_id': self.id}
    #     return action

    # @api.multi
    # def action_view_quotation_product_tree(self):
    #     action = self.env.ref('we_manufacture.action_metal_quotation_product_tree').read()[0]
    #     action['context'] = {'default_quotation_id': self.id}
    #     return action

    # @api.multi
    # def action_view_quotation_product_form  (self):
    #     action = self.env.ref('we_manufacture.action_metal_quotation_product_form').read()[0]
    #     action['context'] = {'default_quotation_tmpl_id': self.id}
    #     return action

class QuotationTemplateMixin(models.AbstractModel):
    _name='metal.quotation.template.mixin'
    _description='Quotation Template Mixin'

    is_template = fields.Boolean('Is Template', compute='_compute_is_template')
    base=fields.Boolean(string='Base', default=False)
    
    def _compute_is_template(self):
        self.is_template= True

    
    def copy_template_to_quotation(self,quotation_id):
        pass

    
    def _add_template_to_quotation(self,tmpl_name,target_ids,current_in_quotation_ids,quotation_id):
        to_copy=result = [x for x in target_ids if x not in current_in_quotation_ids]
        self.env[tmpl_name].browse(to_copy).copy_template_to_quotation(quotation_id)

class QuotationTemplateInheritMixin(models.AbstractModel):
    _name='metal.quotation.template.inherit.mixin'
    _description='Quotation Template Inherit Mixin'

    quotation_id=fields.Many2one('metal.quotation',ondelete='cascade',string='Quotation')
    is_template=fields.Boolean(string='Is template', compute='_compute_is_template')
    
    def _compute_is_template(self):
        self.is_template= False

class QuotationPriceMixin(models.AbstractModel):
    _name='metal.quotation.price.mixin'
    _description='Quotation Price Mixin'

    qty=fields.Integer('Qty')
    margin=fields.Float('Margin',digits=(6,2))
    price=fields.Float('Price',digits=(6,2),compute='_compute_price',store=True,compute_sudo=True)

    def _compute_price(self):
        pass
    
    def compute_price(self,qty,margin,total_subcontracting_cost,total_preparation_cost,total_operation_cost,total_component_cost,component_margin,st_margin):
        

        price=total_component_cost * (1+component_margin/100) 
        price+=(total_subcontracting_cost) * (1+st_margin/100)
        price+=(total_preparation_cost/qty)
        price+=total_operation_cost

        return price * (1+margin/100)
