from odoo import api, exceptions, fields, models, _

class QuotationCalculationFormatTemplate(models.Model):
    _name='metal.quotation.calculation.format.template'
    _description='Quotation Calculation Format Template'
    _inherit=['we.archive.mixin', 'we.sequence.mixin']
    _order='sequence'
    _sql_constraints = [
        ('dimensions_unique', 'unique (length,width)', "This couple of dimensions already exists !"),
    ]
    length=fields.Integer('Length',required=True)
    width=fields.Integer('Width',required=True)
    reversable=fields.Boolean('Reversable',default=False)
    base=fields.Boolean(string='Base', default=False)
    
    def _compute_is_template(self):
        self.is_template= True

    format_ids=fields.One2many('metal.quotation.calculation.format','format_tmpl_id',string='Formats')
    
    def name_get(self):
        return [(rec.id, '{} - {} x {}'.format(rec.id, rec.length, rec.width)) for rec in self]

    @api.constrains('length','width')
    def _check_dimensions(self):
        for record in self:
            if record.length<0 or record.width<0:
                raise exceptions.ValidationError(_('Dimensions must be greater than 0'))

    
class QuotationCalculationFormat(models.Model):
    _name='metal.quotation.calculation.format'
    _description='Quotation Calculation Format'
    _inherit=['we.archive.mixin', 'we.sequence.mixin']
    _order='sequence'

    def get_default_template_base(self):
        return self.env['metal.quotation.calculation.format.template'].search([('base','=',True)],limit=1).ensure_one()

    length=fields.Integer('Length',required=True)
    width=fields.Integer('Width',required=True)

    enabled=fields.Boolean('Enabled',default=True)
    best=fields.Boolean('Best',compute='_compute_best',store=True)
    selected=fields.Boolean('Selected',default=False)

    state=fields.Selection([('best','Best'),('disabled','Disabled'),('not_best','')],default='not_best',compute='_compute_state',store=True)

    format_x=fields.Integer('Format X',compute='_compute_qties',store=True)
    format_y=fields.Integer('Format Y',compute='_compute_qties',store=True)

    format_tmpl_id=fields.Many2one('metal.quotation.calculation.format.template',string='Format Template',store=True,required=True,ondelete='cascade',default=get_default_template_base)
    calcul_id=fields.Many2one('metal.quotation.calculation',string='Calculation',required=True,store=True,ondelete='cascade',default=lambda self: self.env.context.get('default_calcul_id',False))

    qty_per_sheet=fields.Integer('Qty per sheet',compute='_compute_qties',store=True)
    pct_loss = fields.Float('% Loss',digits=(5,2),compute='_compute_qties',store=True)


    @api.model
    def create(self, vals_list):
        fmt= super().create(vals_list)
        others=self.env['metal.quotation.calculation.format'].search([('calcul_id','=',fmt.calcul_id.ids[0])])
        others.calculate_qty()
        return fmt

    def unlink(self):
        if not self:
            return True
        calcul_id=self.calcul_id.id
        res = super().unlink()
        others=self.env['metal.quotation.calculation.format'].search([('calcul_id','=',calcul_id)])
        others.calculate_qty()
        return res

    @api.depends('length','width','enabled','calcul_id.piece_length','calcul_id.piece_width','calcul_id.gap_x','calcul_id.gap_y','calcul_id.clamp_y')
    def _compute_qties(self):
        self.calculate_qty()

    @api.model
    def calculate_qty(self):
        model=self.env['metal.quotation.calculation.format']
        # records=model.search([('calcul_id','=',self.calcul_id.ids[0])])
        records=self
        for record in records:
            # record.format_tmpl_id=record._origin.format_tmpl_id
            if not record.enabled:
                record.format_x,record.format_y,record.qty_per_sheet,record.pct_loss=0,0,0,0
                continue
            try:
                qty_x = int(record.length / (record.calcul_id.piece_length + record.calcul_id.gap_x))
                qty_y= int( (record.width-record.calcul_id.clamp_y) / (record.calcul_id.piece_width+record.calcul_id.gap_x) )
                record.qty_per_sheet=qty_x*qty_y

                record.pct_loss=(((record.length*record.width)-(record.calcul_id.piece_length*record.calcul_id.piece_width*record.qty_per_sheet))/(record.length*record.width))

                record.format_x=int(record.length/qty_x)
                record.format_y=int(record.length/qty_y)
            except ZeroDivisionError:
                record.qty_per_sheet=0
                record.pct_loss=0
                record.format_x=0
                record.format_y=0

            record.update({'format_x':record.format_x,'format_y':record.format_y,'qty_per_sheet':record.qty_per_sheet,'pct_loss':record.pct_loss})

    @api.depends('pct_loss')
    def _compute_best(self):
        records=self.env['metal.quotation.calculation.format'].search([('calcul_id','=',self.calcul_id.ids[0])])
        first=len(records.filtered(lambda x: x.qty_per_sheet>0 and x.enabled).mapped('id')) == len(records.filtered(lambda x: x.enabled))
        for record in records.filtered(lambda x: x.qty_per_sheet>0 and x.enabled).sorted('pct_loss'):
            record.update({'best':first})
            first=False

    @api.depends('best')
    def _compute_state(self):
        for record in self:
            if not  record.enabled:
                record.state='disabled'
            elif record.best:
                record.state='best'
            else:
                record.state='not_best'
            

    
class QuotationCalcul(models.Model):
    _name='metal.quotation.calculation'
    _description='Quotation Calculation'
    _inherit=['we.archive.mixin', 'we.sequence.mixin']

    piece_length=fields.Integer('Piece Length',default=0,required=True)
    piece_width=fields.Integer('Piece Width',default=0,required=True)
    piece_thickness=fields.Float('Piece Thickness',default=0.0,required=True)

    gap_x=fields.Integer('Gap X',default=0,required=True)
    gap_y=fields.Integer('Gap Y',default=0,required=True)

    clamp_y=fields.Integer('Clamp Y',default=0,required=True)

    format_ids=fields.One2many('metal.quotation.calculation.format','calcul_id',string='Formats')

    product_line_id=fields.Many2one('metal.quotation.product.line',string='Operation',required=True,ondelete='cascade',default=lambda self: self.env.context.get('default_product_line_id',False))

    @api.model
    def create(self, vals_list):
        calcul= super().create(vals_list)
        fmts=self.env['metal.quotation.calculation.format.template'].search([('base','=',False)])
        datas=[]
        for fmt in fmts:
            data={
                'calcul_id':calcul.id,
                'format_tmpl_id':fmt.id,
                'length':fmt.length,
                'width':fmt.width,
            }
            datas.append(data)
            if fmt.reversable:
                data={
                    'calcul_id':calcul.id,
                    'format_tmpl_id':fmt.id,
                    'length':fmt.width,
                    'width':fmt.length,
                }
                datas.append(data)
        calcul.format_ids.create(datas)
        return calcul

    # def add_format(self):
    #     self.ensure_one()
    #     return {
    #         'name': 'Add a format',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'metal.add.format.to.calcul.wizard',
    #         'context': {'default_calcul_id': self.id},
    #         'target': 'new',
    #     }

# class QuotationCalculWorkcenter(models.Model):
#     _name='metal.quotation.calculation.workcenter'
#     _description='Quotation Calculation Workcenter'
#     _inherit=['we.archive.mixin', 'we.sequence.mixin']
#     workcenter_id=fields.Many2one('mrp.workcenter',string='Workcenter',required=True)

class QuotationCalculateCutting(models.Model):
    _name='metal.quotation.calculation.cutting'
    _description='Quotation Calculation Cutting'
    _inherit=['we.archive.mixin', 'we.sequence.mixin']
    


    thickness=fields.Float('Thickness',default=0.0,required=True)
    # gas=fields.Selection([('air','Air'),('argon','Argon'),('helium','Helium'),('nitrogen','Nitrogen'),('oxygen','Oxygen'),('carbon_dioxide','Carbon Dioxide'),('carbon_monoxide','Carbon Monoxide'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride'),('carbon_monofluoride','Carbon Monofluoride'),('carbon_tetrafluoride','Carbon Tetrafluoride')])
    material_id=fields.Many2one('metal.quotation.material',string='Material',required=True,default=lambda self: self.env.context.get('default_material_id',False))
    gas=fields.Selection([('oxygen','O2'),('azote','NA')],string='Gas',default='oxygen',required=True)
    length=fields.Integer('Length',default=0,required=True)
    qty_small=fields.Integer('Qty Small',default=0,required=True)
    qty_boot=fields.Integer('Qty Boot',default=0,required=True)
    vapo=fields.Boolean('Vapo',default=False)
    workcenter_id=fields.Many2one('mrp.workcenter',string='Workcenter',required=True,readonly=True,default=lambda self: self.env.context.get('default_workcenter_id',False))

    low_speed=fields.Integer('Low Speed',compute="_compute_speed",store=True)
    high_speed=fields.Integer('High Speed',compute="_compute_speed",store=True)
    product_line_id=fields.Many2one('metal.quotation.product.line',string='Operation',required=True,readonly=True,ondelete='cascade',default=lambda self: self.env.context.get('default_product_line_id',False))

    value=fields.Float('Value',digits=(8,5), compute='_compute_value',store=True)


    @api.depends('low_speed','high_speed','length','qty_small','qty_boot','vapo')
    def _compute_value(self):
        for record in self:
            record.value= record.calculate_value()

    
    def calculate_value(self):
        record=self
        v1=record.length/record.high_speed/60 if record.high_speed else 0
        v2=record.qty_small*40/record.low_speed/60 if record.low_speed else 0
        v3=record.qty_boot*record.thickness*0.00027
        v4=((record.length+(record.qty_small+10))/8000)/60 if record.vapo else 0
        record.value=v1+v2+v3+v4
        return record.value 

    @api.depends('thickness','gas','material_id','workcenter_id')
    def _compute_speed(self):
        wk_model=self.env['mrp.workcenter.cutting.speed']
        for record in self:
            if record.workcenter_id.id and record.material_id.id :
                domain=[]
                domain.append(('workcenter_id','=',record.workcenter_id.id))
                domain.append(('gas','=',record.gas))
                domain.append(('thickness','=',record.thickness))
                domain.append(('material_id','=',record.material_id.volumic_mass_id.id))
                speed=wk_model.search(domain,limit=1)
                if speed:
                    record.low_speed=speed.speed_int
                    record.high_speed=speed.speed_ext
                    continue
                record.low_speed=0
                record.high_speed=0
            
                