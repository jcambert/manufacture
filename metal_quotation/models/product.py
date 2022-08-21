from asyncore import read
import string
from odoo import api, exceptions, fields, models, _

class QuotationProduct(models.Model):
    _name="metal.quotation.product"
    _description="Quotation Product"
    _order = "name, id"
    _inherit=['we.archive.mixin','we.color.mixin','metal.quotation.mixin']
    _sql_constraints=[('name_uniq', 'unique(name,quotation_id)', 'Name must be unique for this quotation!')]
    name=fields.Char(string='Name', required=True,index=True)
    description = fields.Char(string='Description')
    revision=fields.Char(string='Revision')
    quotation_id=fields.Many2one('metal.quotation',ondelete='cascade',string='Quotation',required=True,default=lambda self: self.env.context.get('default_quotation_id',False))
    default_quotation_id=fields.Boolean(string='Default Quotation',store=False,compute='_compute_default_quotation_id')
    subcontract_ids=fields.One2many('metal.quotation.product.subcontract','product_id',string='Subcontracts')
    components_ids=fields.One2many('metal.quotation.product.component','product_id',string='Components')
    line_ids=fields.One2many('metal.quotation.product.line','product_id',string='Lines')
    price_ids= fields.One2many('metal.quotation.product.price','product_id',string='Prices')
    qty=fields.Integer(string='Quantity',default=1)

    total_subcontracting_cost=fields.Float(string='Total Subcontracting Cost',compute_sudo=True,compute='_compute_costs',store=True)
    total_component_cost=fields.Float(string='Component Cost', compute='_compute_costs',compute_sudo=True,store=True)
    total_preparation_cost=fields.Float(string='Total Preparation Cost',store=True,compute_sudo=True,compute='_compute_costs')
    total_operation_cost=fields.Float(string='Total Operation Cost',store=True,compute_sudo=True,compute='_compute_costs')

    @api.constrains('qty')
    def _check_qty(self):
        for record in self:
            if record.qty <= 0:
                raise exceptions.ValidationError("Qty must be greater than 0")

    @api.depends('quotation_id')
    def on_quotation_changed(self):
        self.ensure_one()
        self.material_margin = self.quotation_tmpl_id.material_margin
        self.component_margin = self.quotation_tmpl_id.component_margin
        self.be_time = self.quotation_tmpl_id.be_time
        self.be_cost = self.quotation_tmpl_id.be_cost
        self.fad_cost = self.quotation_tmpl_id.fad_cost
        self.tool_cost = self.quotation_tmpl_id.tool_cost
        self.st_margin = self.quotation_tmpl_id.st_margin
        return True


    @api.depends('subcontract_ids','line_ids','components_ids','qty')
    def _compute_costs(self):
        for record in self:
            record.total_subcontracting_cost = sum(record.subcontract_ids.mapped('cost'))*record.qty
            record.total_preparation_cost = sum(record.line_ids.mapped('preparation_cost'))*record.qty
            record.total_operation_cost = sum(record.line_ids.mapped('operation_cost'))*record.qty
            record.total_component_cost = sum(record.components_ids.mapped('cost'))*record.qty

    def _compute_default_quotation_id(self):
        for record in self:
            record.default_quotation_id=bool(self.env.context.get('default_quotation_id',False))
    
class QuotationProductLine(models.Model):
    _name='metal.quotation.product.line'
    _description='Quotation Product Line'


    description=fields.Char(string='Description')
    nb=fields.Integer(string='Nb',help='Number of Action')
    quotation_operation_id=fields.Many2one('metal.quotation.operation',ondelete='cascade',string='Operation',domain="[('quotation_id','=',quotation_id)]")
    
    quotation_id=fields.Integer(related='product_id.quotation_id.id',string='Quotation')
    workcenter_id=fields.Many2one('mrp.workcenter',string='Workcenter',related='quotation_operation_id.workcenter_id')

    operation_time=fields.Float(string='Operation Time',help='Operation Time',store=True,compute_sudo=True,compute='on_quotation_operation_changed',digits=(6,4))
    operation_cost=fields.Float(string='Operation Cost',help='Operation Cost',store=True,compute_sudo=True,compute='on_quotation_operation_changed')
    
    piece_cadence=fields.Float(string='Cadence',help='Cadence',store=True,compute_sudo=True,compute='compute_costs')
    piece_time=fields.Float(string='Piece Time',help='Piece Time',store=True,compute_sudo=True,compute='compute_costs')

    product_id=fields.Many2one('metal.quotation.product',ondelete='cascade',string='Product')

    preparation_time=fields.Float(string='Preparation Time',help='Preparation Time',digits=(6,4))
    preparation_cost=fields.Float(string='Preparation Cost',help='Preparation Cost',store=True,compute_sudo=True,compute='compute_costs')

    calculated=fields.Boolean(string='Calculated',related='quotation_operation_id.operation_tmpl_id.workcenter_id.calculated',store=False)

    calculation_ids=fields.One2many('metal.quotation.calculation','product_line_id',string='Calculations')
    def name_get(self):
        return [(rec.id, '{} - {} - {}'.format(rec.id, rec.product_id, rec.quotation_operation_id)) for rec in self]

    @api.depends('quotation_operation_id','nb','preparation_time')
    def compute_costs(self):
        for record in self:
            record.operation_time = record.quotation_operation_id.operation_base_time * record.nb
            record.operation_cost = record.quotation_operation_id.operation_cost * record.operation_time

            record.piece_time = record.operation_time*60

            record.piece_cadence = 60/record.piece_time if record.piece_time>0 else 0

            record.preparation_cost = record.quotation_operation_id.preparation_cost * record.preparation_time
            return True
    
    @api.onchange('quotation_operation_id')
    def on_quotation_operation_changed(self):
        self.ensure_one()
        self.preparation_time = self.quotation_operation_id.preparation_time
        pass

    def show_format_calculate_view(self):
        self.ensure_one()
        try:
            calcul_id=self.env['metal.quotation.calculation'].search([('product_line_id','=',self.id)],limit=1).ensure_one()[0]
        except ValueError:
            calcul_id=self.env['metal.quotation.calculation'].create({'product_line_id':self.id})
        return {
            'name': 'Add a format',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.quotation.calculation',
            'res_id': calcul_id.id,
            'context': {'default_product_line_id': self.id,'active_id':calcul_id.id},
            'domain': [('id', '=', calcul_id.id)],
            'target': 'current',
        }

    def show_speed_calculate_view(self):
        self.ensure_one()
        try:
            calcul_id=self.env['metal.quotation.calculation.cutting'].search([('product_line_id','=',self.id)],limit=1).ensure_one()[0]
        except ValueError:
            material_id=self.env['metal.quotation.material'].search([('quotation_id','=',self.quotation_id)],limit=1).ensure_one()[0]
            thickness=self.env['metal.quotation.calculation'].search([('product_line_id','=',self.id)],limit=1).ensure_one()[0]
            calcul_id=self.env['metal.quotation.calculation.cutting'].create({'product_line_id':self.id,'workcenter_id':self.workcenter_id.id,'material_id':material_id.id,'thickness':thickness.piece_thickness})
        return {
            'name': 'Add a speed',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.quotation.calculation.cutting',
            'res_id': calcul_id.id,
            'context': {'default_product_line_id': self.id,'default_workcenter_id':self.workcenter_id.id,'default_material_id':material_id.id,'active_id':calcul_id.id},
            'domain': [('id', '=', calcul_id.id)],
            'target': 'current',
        }

class QuotationProductComponent(models.Model):
    _name='metal.quotation.product.component'
    _description='Product Component'

    nb=fields.Float(string='Nb',help='Number of Component',digits=(6,4))
    cost=fields.Float(string='Component Cost',help='Component Cost',store=True,compute_sudo=True,compute='compute_costs')
    product_id = fields.Many2one('metal.quotation.product',string='Product',required=True)
    component_id = fields.Many2one('metal.quotation.component',string='Component',required=True,domain=[('is_template','=',False)])
    quotation_id=fields.Many2one(related='product_id.quotation_id',string='Quotation')
    name = fields.Char(related='component_id.name',string='Name')
    description = fields.Text(related='component_id.description',string='Description')
    unit_cost=fields.Float(related='component_id.unit_cost',string='Unit Cost')
    is_template=fields.Boolean(related='component_id.is_template',string='Is Template')

    @api.depends('nb','component_id.unit_cost')
    def compute_costs(self):
        for record in self:
            record.cost = record.component_id.unit_cost * record.nb
            return True

