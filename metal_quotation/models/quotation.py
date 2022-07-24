from odoo import api, exceptions, fields, models, _




class QuotationTemplate(models.Model):
    _name = 'metal.quotation.template'
    _description = 'Quotation Template'
    _order = "sequence desc, id"
    _inherit=['we.sequence.mixin','we.archive.mixin','we.company.currency.mixin','we.color.mixin','mail.thread', 'mail.activity.mixin', 'image.mixin']
    _check_company_auto = True
    

    sequence=fields.Integer(string='Sequence', default=1)
    date_order = fields.Datetime(string='Quotation Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent quotation")
    name=fields.Char(string='Name', required=True)
    description = fields.Char('Description')
    quotation_count=fields.Integer(string='Quotation Count', compute='_compute_quotation_count')
    material_margin = fields.Integer( string="Material Margin")
    component_margin = fields.Integer( string="Component Margin")
    be_time = fields.Integer( string="Default Etude Time")
    be_cost = fields.Monetary( string="Default Be Cost")
    fad_cost = fields.Monetary( string="Default FAD Cost")
    tool_cost = fields.Monetary( string="Default Tool Cost")
    st_margin = fields.Integer( string="Default ST Margin")

    
    

    def _compute_quotation_count(self):
        for record in self:
            record.quotation_count = self.env['metal.quotation'].search_count([('quotation_tmpl_id', '=', record.id)])

    def create_quotation(self):
        self.ensure_one()
        quotation = self.env['metal.quotation'].create({
            'name': self.name,
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
    
    _inherit=['we.archive.mixin','we.company.currency.mixin','we.color.mixin','we.state.mixin','we.priority.mixin','mail.thread', 'mail.activity.mixin', 'image.mixin']
    _sequence_name='metal.quotation'

    @api.model
    def _get_default_quotation_tmpl(self):
        return self.env['metal.quotation.template'].search([], limit=1)

    quotation_tmpl_id = fields.Many2one('metal.quotation.template', 'Quotation Template',default=_get_default_quotation_tmpl,auto_join=True, index=True, ondelete="cascade", required=True)
    
    name = fields.Char('Number', copy=False, readonly=True, default=lambda x: _('New'))
    revision = fields.Integer(string='Revision', default=0,copy=False,readonly=True)

    description = fields.Char('Description')

    date_order = fields.Datetime(string='Quotation Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent quotation")
    description = fields.Char('Description')
    material_margin = fields.Integer( string="Material Margin")
    component_margin = fields.Integer( string="Component Margin")
    be_time = fields.Integer( string="Default Etude Time")
    be_cost = fields.Monetary( string="Default Be Cost")
    fad_cost = fields.Monetary( string="Default FAD Cost")
    tool_cost = fields.Monetary( string="Default Tool Cost")
    st_margin = fields.Integer( string="Default ST Margin")

    product_ids=fields.One2many('metal.quotation.product','quotation_id',string='Products')
    # @api.model
    # def default_get(self, fields):
    #     res = super().default_get(fields)
    #     if not res.get('quotation_tmpl_id'):
    #         tmp= self.env['metal.quotation.template'].search([],limit=1).id
    #         res['quotation_tmpl_id'] =tmp 
    #     return res
   
    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
           values['name'] = self.env['ir.sequence'].next_by_code(self._sequence_name) or _('New')
        res = super(Quotation, self).create(values)
        return res
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