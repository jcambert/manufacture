from operator import index
from odoo import api, exceptions, fields, models, _
import re

list_comma=re.compile('^\d(,\d)*(\d(,\d)*)*$')

class QuotationTemplate(models.Model):
    _name = 'metal.quotation.template'
    _description = 'Quotation Template'
    _order = "sequence desc, id"
    _inherit=['we.sequence.mixin','we.archive.mixin','we.color.mixin','mail.thread', 'mail.activity.mixin', 'image.mixin','metal.quotation.mixin']
    _check_company_auto = True
    

    sequence=fields.Integer(string='Sequence', default=1)
    date_order = fields.Datetime(string='Quotation Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent quotation")
    name=fields.Char(string='Name', required=True)
    description = fields.Char('Description')
    quotation_count=fields.Integer(string='Quotation Count', compute='_compute_quotation_count')
    
    quantities=fields.Char(string='Quantities',help='Comma separated list of quantites')
    margins=fields.Char(string='Margins',help='Comma separated list of margins')

    note=fields.Text('Note')
    @api.constrains('quantities','margins')
    def check_prices(self):
        
        for record in self:
            if record.quantities:
                if not list_comma.match(record.quantities):
                    raise exceptions.ValidationError('Quantities must be int comma separated list')
                quantities=record.quantities.split(',')
                for quantity in quantities:
                    if int(quantity) < 0:
                        raise exceptions.ValidationError('Quantities must be positive')
                if not list_comma.match(record.margins):
                    raise exceptions.ValidationError('Margins must be int comma separated list')
                margins=record.margins.split(',')
                for margin in margins:
                    if int(margin) < 0:
                        raise exceptions.ValidationError('Margins must be positive')
                
                if len(quantities) != len(margins):
                    raise exceptions.ValidationError('Quantities and Margins must be same length')

    def _compute_quotation_count(self):
        for record in self:
            record.quotation_count = self.env['metal.quotation'].search_count([('quotation_tmpl_id', '=', record.id)])

    def create_quotation(self):
        self.ensure_one()
        quotation = self.env['metal.quotation'].create({
            'name': _('New'),
            'quotation_tmpl_id': self.id,
            'date_order': self.date_order,
            'description': self.description,
            'material_margin': self.material_margin,
            'component_margin': self.component_margin,
            'be_time': self.be_time,
            'be_cost': self.be_cost,
            'fad_cost': self.fad_cost,
            'tool_cost': self.tool_cost,
            'st_margin': self.st_margin,
        })
        return {
            'name': _('Quotation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.quotation',
            'res_id': quotation.id,
            'target': 'current',
            'context': {'default_quotation_tmpl_id': self.id}
        }
class Quotation(models.Model):
    _name = 'metal.quotation'
    _description = 'Quotation'
    _order = "id"
    
    _inherit=[ 'we.archive.mixin','we.color.mixin','we.priority.mixin','mail.thread', 'mail.activity.mixin', 'image.mixin','metal.quotation.mixin','we.company.currency.mixin']
    _sequence_name='metal.quotation'

    @api.model
    def _get_default_quotation_tmpl(self):
        return self.env['metal.quotation.template'].search([], limit=1)

    quotation_tmpl_id = fields.Many2one('metal.quotation.template', 'Quotation Template',default=_get_default_quotation_tmpl,auto_join=True, index=True, ondelete="cascade", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done','Done'),
        ('locked', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft',compute='_compute_state')

    name = fields.Char('Number', copy=False, readonly=True, default=lambda x: _('New'))
    revision = fields.Integer(string='Revision', default=0,copy=False,readonly=True)

    description = fields.Char('Description')
    description2 = fields.Char('Description2')

    date_order = fields.Datetime(string='Quotation Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent quotation")

    product_ids=fields.One2many('metal.quotation.product','quotation_id',string='Products')
    product_count=fields.Integer(string='Product Count', compute='_compute_product_count')

    operation_ids=fields.One2many('metal.quotation.operation','quotation_id',string='Operations')

    component_ids=fields.One2many('metal.quotation.component','quotation_id',string='Components')

    material_ids=fields.One2many('metal.quotation.material','quotation_id',string='Materials')

    prices_ids=fields.One2many('metal.quotation.price','quotation_id',string='Prices')

    total_subcontracting_cost=fields.Float(string='Subcontracting Cost', compute='_compute_total_subcontracting_cost',compute_sudo=True,store=True)

    total_component_cost=fields.Float(string='Component Cost', compute='_compute_total_component_cost',compute_sudo=True,store=True)

    # total_material_cost=fields.Float(string='Material Cost', compute='_compute_total_material_cost',compute_sudo=True,store=True)

    total_preparation_cost=fields.Float(string='Preparation Cost', compute='_compute_total_preparation_cost',compute_sudo=True,store=True)

    total_operation_cost = fields.Float(string='Operation Cost', compute='_compute_total_operation_cost',compute_sudo=True,store=True)

    quotation_note=fields.Html(string="Footer Note")
    
    estimator=fields.Many2one('res.users',string='Estimator',required=True,default=lambda self: self.env.user)

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
           values['name'] = self.env['ir.sequence'].next_by_code(self._sequence_name) or _('New')
        res = super(Quotation, self).create(values)
        #copy template operation
        # tpls=self.env['metal.quotation.operation'].search([]).copy_to_quotation(res.id)
        res.use_operations()

        #copy template component
        tpls= self.env['metal.quotation.component'].search([]).copy_to_quotation(res.id)

        #copy template material
        res.use_materials()
        
        quantities=res.quotation_tmpl_id.quantities.split(',') if res.quotation_tmpl_id.quantities else []
        margins=res.quotation_tmpl_id.margins.split(',') if  res.quotation_tmpl_id.margins else []
        

        for q,m in zip(quantities,margins):
            self.env['metal.quotation.price'].create({
                'quotation_id':res.id,  
                'qty':q,
                'margin':m
            })
        
        res.use_materials()
        return res

    @api.depends('product_ids.total_subcontracting_cost')
    def _compute_total_subcontracting_cost(self):
        for record in self:
            record.total_subcontracting_cost = sum(record.product_ids.mapped('total_subcontracting_cost'))

    @api.depends('product_ids.total_component_cost')
    def _compute_total_component_cost(self):
        for record in self:
            record.total_component_cost = sum(record.product_ids.mapped('total_component_cost'))

    @api.depends('product_ids.total_operation_cost')
    def _compute_total_operation_cost(self):
        for record in self:
            record.total_operation_cost = sum(record.product_ids.mapped('total_operation_cost'))

    @api.depends('product_ids.total_preparation_cost')
    def _compute_total_preparation_cost(self):
        for record in self:
            record.total_preparation_cost = sum(record.product_ids.mapped('total_preparation_cost'))

    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)

    @api.depends('product_count')
    def _compute_state(self):
        for record in self:
            if record.product_count > 0:
                record.state ='running'
            else:
                record.state ='draft'

    @api.onchange('quotation_tmpl_id')
    def on_quotation_template_change(self):
        self.ensure_one()
        # self.name = self.quotation_tmpl_id.name
        self.description = self.quotation_tmpl_id.description
        self.material_margin = self.quotation_tmpl_id.material_margin
        self.component_margin = self.quotation_tmpl_id.component_margin
        self.be_time = self.quotation_tmpl_id.be_time
        self.be_cost = self.quotation_tmpl_id.be_cost
        self.fad_cost = self.quotation_tmpl_id.fad_cost
        self.tool_cost = self.quotation_tmpl_id.tool_cost
        self.st_margin = self.quotation_tmpl_id.st_margin
        self.note = self.quotation_tmpl_id.note
        
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if not default.get('revision', False) :
            default['name'] = self.env['ir.sequence'].next_by_code(self._sequence_name) or _('New')
        else:
            default['name']="%s-%s"%(self.name.split("-")[0],default['revision'])

        return super(Quotation, self).copy(default)

    
    def copy_revision(self):
        self.ensure_one()
        quotation= self.copy({'revision': self.revision+1})
        return {
            'name': _('Quotation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.quotation',
            'res_id': quotation.id,
            'target': 'main',
            'context': {}
        }

    def add_product(self):
        self.ensure_one()
        return {
            'name': 'Add Product To Quotation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.add.product.to.quotation.wizard',
            'context': {'default_quotation_id': self.id},
            'target': 'new',
        }
        # product = self.env['metal.quotation.product'].create({
        #     'name': _('New'),
        #     'quotation_id': self.id,
        #     'description': '',
        #     'material_margin': self.material_margin,
        #     'component_margin': self.component_margin,
        #     'be_time': self.be_time,
        #     'be_cost': self.be_cost,
        #     'fad_cost': self.fad_cost,
        #     'tool_cost': self.tool_cost,
        #     'st_margin': self.st_margin,
        # })
        # return {
        #     'name': 'view.product.action',
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'metal.quotation.product',
        #     'res_id': product.id,
        #     'target': 'current',
        #     'context': {'default_quotation_id': self.id}
        # }
    def load_materials_popup(self):
        self.ensure_one()
        return {
            'name': 'Load Materials',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.add.materials.templates.quotation.wizard',
            'context': {'default_quotation_id': self.id},
            'target': 'new',
        }
    
    def use_materials(self):
        self.ensure_one()
        self.env['metal.quotation.material.template'].add_template_to_quotation(self.id)


    def load_operations_popup(self):
        self.ensure_one()
        return {
            'name': 'Load Operations',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.add.operations.templates.quotation.wizard',
            'context': {'default_quotation_id': self.id},
            'target': 'new',
        }
    
   
    def use_operations(self):
        self.ensure_one()
        self.env['metal.quotation.operation.template'].add_template_to_quotation(self.id)

    def load_components_popup(self):
        self.ensure_one()
        return {
            'name': 'Load Operations',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.add.components.templates.quotation.wizard',
            'context': {'default_quotation_id': self.id},
            'target': 'new',
        }
    
    def use_components(self):
        self.ensure_one()
        self.env['metal.quotation.component.template'].add_template_to_quotation(self.id)
        
class QuotationPrice(models.Model):
    _name = 'metal.quotation.price'
    _description = 'Quotation Price'
    _inherit=['metal.quotation.price.mixin']

    # qty=fields.Integer('Qty')
    # margin=fields.Float('Margin',digits=(6,2))
    # price=fields.Float('Price',digits=(6,2),compute='_compute_price',store=True,compute_sudo=True)
    quotation_id = fields.Many2one('metal.quotation', string='Quotation', ondelete='cascade')
    
    @api.depends('qty','margin','quotation_id','quotation_id.total_subcontracting_cost','quotation_id.total_preparation_cost','quotation_id.total_operation_cost','quotation_id.total_component_cost','quotation_id.component_margin','quotation_id.st_margin')
    def _compute_price(self):
        for record in self:
            total_subcontracting_cost = record.quotation_id.total_subcontracting_cost
            total_preparation_cost=record.quotation_id.total_preparation_cost
            total_operation_cost=record.quotation_id.total_operation_cost
            total_component_cost=record.quotation_id.total_component_cost

            component_margin=record.quotation_id.component_margin
            st_margin=record.quotation_id.st_margin

            # price=total_component_cost * (1+component_margin/100) 
            # price+=(total_subcontracting_cost) * (1+st_margin/100)
            # price+=(total_preparation_cost/record.qty)
            # price+=total_operation_cost

            # record.price = price * (1+record.margin/100)
            record.price = self.compute_price(record.qty,record.margin,total_subcontracting_cost,total_preparation_cost,total_operation_cost,total_component_cost,component_margin,st_margin)
        return True