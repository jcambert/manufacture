# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
DEFAULT_TYPE_ID='default_type_id'

class Eco(models.Model):
    _name = 'mrp.plm.eco'
    _description='Ordre de Modification Technique (OMT)'
    _inherit = ['mail.activity.mixin', 'mail.thread.cc', 'mail.alias.mixin',
                'we.archive.mixin', 'we.sequence.mixin', 'we.company.mixin', 'we.color.mixin','we.kanban.mixin','we.priority.mixin']
    
    _order = "sequence , name, id"
    _check_company_auto = True
    _sequence_name='mrp.plm.eco'
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        type_id = self.env.context.get(DEFAULT_TYPE_ID) or False
        
        return self.stage_find(type_id, [('folded', '=', False), ('final_stage', '=', False)])

    allow_apply_change=fields.Boolean('Allow apply change',compute='_compute_allow_apply_change',help="Show allowed apply changes")
    allow_change_kanban_state=fields.Boolean('Allow change kanban state',compute='_compute_allow_change_kanban_state',help="Show allowed change kanban state")
    allow_change_stage=fields.Boolean('Allow change state', compute='_compute_allow_change_stage', help="Allowing changing state")
    approval_ids=fields.One2many('mrp.plm.eco.approval','eco_id',help="validation approvals")
    bom_change_ids=fields.One2many('mrp.plm.eco.bom.change','eco_id',readonly=True,help='OMT Modification')
    bom_id=fields.Many2one('mrp.bom',string='Bom')
    bom_rebase_ids=fields.One2many('mrp.plm.eco.bom.change','rebase_id',string='Bom rebase')
    current_bom_id=fields.Many2one('mrp.bom',string='Current Bom')
    
    displayed_image_attachment_id=fields.Many2one('ir.attachment',string='Attached piece')
    displayed_image_id=fields.Many2one('mrp.document',string='Image')

    effectivity=fields.Selection([('asap','Asap'),('date','to date')],'Effective date ',help="Date to do task",default='asap')
    effectivity_date=fields.Date('Effective date')
    
    legend_blocked = fields.Char(related='stage_id.legend_blocked', readonly=True)
    legend_done = fields.Char(related='stage_id.legend_done', readonly=True)
    legend_normal=fields.Char(related='stage_id.legend_normal', readonly=True)

    mrp_document_count=fields.Integer('Attached document Nb',compute='_compute_mrp_document_count')
    mrp_document_ids=fields.One2many('mrp.document', 'res_id',help='Attached documents')
    my_activity_date_deadline=fields.Date('My effective date',help="My effective date dead line",readonly=True)
    name=fields.Char('Name',required=True)
    full_name=fields.Char('Name',compute='_compute_full_name')
    new_bom_id = fields.Many2many('mrp.bom')
    new_bom_revision=fields.Integer('BOM revision')
    note=fields.Text('Internal Notes')
    previous_change_ids=fields.One2many('mrp.plm.eco.bom.change','rebase_id',string='Previous changed',readonly=True)
    product_tmpl_id=fields.Many2one('product.template',string='Article')
    sequence=fields.Char(string='Sequence',required=True,copy=False,readonly=True,default=lambda self:_('New'))
    routing_change_ids=fields.One2many('mrp.plm.eco.routing.change','eco_id',string='Routing change')
    stage_id=fields.Many2one('mrp.plm.eco.stage' ,
        ondelete='restrict',
        help="Stage",
        compute='_compute_stage_id',
        default=_get_default_stage_id,
        group_expand='_read_group_stage_names',
        index=True, tracking=True,copy=False,readonly=False, store=True,
        domain="[ ('type_ids', 'in', type_id)]"
        )
    stage_name=fields.Char(related='stage_id.name',string='Stage name')
    state=fields.Selection(
        [('confirmed','Confirmed'), ('progress','Progress'),('rebase','Rebase'),('conflict','Conflict'),('done','Done')],
        string='State',
        default='confirmed',
        copy=False,required=True,help="Statut",tracking=True,store=True
        )
    tag_ids = fields.Many2many('mrp.plm.eco.tag' , 'mrp_plm_eco_tags_rel', 'plm_id', 'tag_id', string='Tags')
    type=fields.Selection([('product','Product only'),('bom','BOM'),('routing','Routing'),('both','Both')],default='product',string='Apply to')
    type_id=fields.Many2one('mrp.plm.eco.type','Type',ondelete='restrict',required=True,help="Type",store=True)
    type_id_name=fields.Char(related='type_id.name',string='Type name')
    user_can_approve=fields.Boolean('Can approve',compute='_compute_user_can_approve_or_reject',help="User can approve")
    user_can_reject=fields.Boolean('Can reject',compute='_compute_user_can_approve_or_reject',help="User can reject")
    user_id=fields.Many2one('res.users','Responsible',help="User responsible", default=lambda self: self.env.user, tracking=True)

    sale_ok = fields.Boolean('Can be Sold',related='product_tmpl_id.sale_ok',readonly=True)
    purchase_ok = fields.Boolean('Can be Purchased',related='product_tmpl_id.purchase_ok',readonly=True)
    can_manufacture=fields.Boolean('Can manufacture',help="Can manufacture")
    can_purchase=fields.Boolean('Can purchase',help="Can purchase")

    @api.model
    def default_get(self, fields):
        vals = super(Eco, self).default_get(fields)
        art=self.env['product.template'].search([],limit=1)
        vals['product_tmpl_id']=art.id
        return vals

    def name_get(self):
        return [(eco.id, '%s:%s' % (eco.sequence, eco.name ) ) for eco in self]

    @api.model
    def create(self, vals):
        
        res= super(Eco,self).create(vals)
        if res and 'stage_id' in vals:
            self.createApprovals(res.id, vals['stage_id'],res.type_id.id)
            self.flush()
        return res

    
    def write(self,vals):
        res = super(Eco,self).write(vals)
        return res

    def _compute_full_name(self):
        for eco in self:
            eco.full_name='%s:%s' % (eco.sequence, eco.name )

    @api.model
    def createApprovals(self,eco_id,stage_id,type_id):
        stage=self.env['mrp.plm.eco.stage'].search([('id','=',stage_id), ('type_ids','=',type_id)])
        result=[]
        if stage :
            print('stage',stage.name)
            for approval in stage.approval_template_ids:
                result.append(self.env['mrp.plm.eco.approval'].create({'eco_id':eco_id,'template_stage_id':approval.stage_id.id,'approval_template_id':approval.id}).id)
        return result
        #if stage.exists():
        #    for t in stage.approval_template_ids:
        #        self.env['mrp.plm.eco.approval'].create({
        #        'approval_template_id':t.id,
        #        'eco_id':eco_id,
        #        'template_stage_id':stage.id
        #        })
    @api.model
    def default_get(self, default_fields):
        vals = super(Eco, self).default_get(default_fields)

        return vals
    
    @api.depends('type_id')
    def _compute_stage_id(self):
        for eco in self:
            eco.stage_id = eco.stage_find(eco.id, [('folded', '=', False), ('final_stage', '=', False)])
            
    @api.depends('state')
    def _compute_allow_change_stage(self):
        for eco in self:
            eco.allow_change_stage=eco.state not in ['confirmed','done']

    def _compute_mrp_document_count(self):
        for eco in self:
            eco.mrp_document_count=0

    @api.depends('stage_id')
    def _compute_allow_apply_change(self):
        for eco in self:
            eco.allow_apply_change= eco.stage_id.allow_apply_change
            if eco.id:
                #Recalculate product's ECO Count
                eco.product_tmpl_id.recalcul_eco_count()
    
    @api.depends('state','stage_id','approval_ids.status')
    def _compute_user_can_approve_or_reject(self):
        for record in self:
            record.user_can_approve=False
            record.user_can_reject=False

            my_pendings=record.approval_ids.filtered(lambda x: self.env.user in x.required_user_ids and x.is_pending)
            my_last_not_pending=record.approval_ids.filtered(lambda x: self.env.user in x.required_user_ids and not x.is_pending)

            if any(my_pendings):
                record.user_can_approve=True
                record.user_can_reject=True
            elif len(my_last_not_pending)>0:
                if my_last_not_pending[0].status=='approved':
                    record.user_can_approve=False
                    record.user_can_reject=True
                elif my_last_not_pending[0].status=='rejected':
                    record.user_can_approve=True
                    record.user_can_reject=False
                    
            
            pendings=record.approval_ids.filtered(lambda x:  x.is_pending)
            if any(pendings):
                record.kanban_state='blocked'
            # domain=[('id','in',record.approval_ids.ids)]
            # groups = self.env['mrp.plm.eco.approval'].read_group(domain, ['id','status'], ['name'])
            # pass
            

        

    @api.onchange('stage_id')
    def on_stage_change(self):
        
        if len(self.ids)==0:
            return
        self.ensure_one()

        if not self.allow_change_stage:
            self.write({'stage_id':self._origin.stage_id.id})
            self.flush()

            if self.state=='done':
                raise UserError(_("This ECO is closed. You can't change the stage."))
            elif self.state!='progress':
                raise UserError(_("You must start revision, before changing state"))
        rec=self._origin
        groups={}
        for approval in rec.approval_ids.filtered(lambda x: x.eco_stage_id.id==rec.stage_id.id):

            if approval.approval_template_id.id in groups:
                continue
            if approval.is_approved:
                groups[approval.approval_template_id.id]=False
            else:
                groups[approval.approval_template_id.id]= (approval.is_pending or approval.is_rejected) and approval.approval_template_id.approval_type=='mandatory'

       
        groups = {k: v for k, v in groups.items() if v}
        if len(groups)>0:
            self.write({'stage_id':rec.stage_id.id})
            raise UserError(_("You must approve or reject all approvals before changing state"))
            


        
           
        #create new approvals if needed    
        self.createApprovals(self._origin.id,self.stage_id.id,self.type_id.id) 
        

        

        if not self.approval_ids.need_approvals():
            self.kanban_state='done'
            return

    def action_new_revision(self):
        self.ensure_one()
        if self.state=='confirmed':
            self.write({'state':'progress','kanban_state':'normal'})
            self.user_can_approve=True
            self.user_can_reject=True
        return True


    
    def apply_rebase(self):
        pass
    def conflict_resolve(self):
        pass
    
    def approve(self):
        self.ensure_one()
        if not self.user_can_approve:
            return
        eligibles=self.approval_ids.filtered(lambda x:x.eco_stage_id.id==self.stage_id.id and x.is_pending and  ( self.env.user in x.required_user_ids ))
        closables=self.approval_ids.filtered(lambda x:x.eco_stage_id.id==self.stage_id.id and (x.is_rejected or x.is_approved) )
        if not eligibles:
            ids=self.createApprovals(self._origin.id,self.stage_id.id,self.type_id.id)
            eligibles=self.env['mrp.plm.eco.approval'].browse(ids)
        # for approval in eligibles:
        eligibles.approve()
        # for approvable in closables:
        closables.close()

        self.flush()
        if self.stage_id.final_stage:
            self. write({'state':'done'})
            # self.kanban_state='blocked'
        return True


    def reject(self):
        self.ensure_one()
        if not self.user_can_reject:
            return
        eligibles=self.approval_ids.filtered(lambda x:x.eco_stage_id.id==self.stage_id.id and x.is_pending and  self.env.user in x.required_user_ids)
        if not eligibles:
            ids=self.createApprovals(self._origin.id,self.stage_id.id,self.type_id.id)
            eligibles=self.env['mrp.plm.eco.approval'].browse(ids)
        
        eligibles.reject()
        
        self.flush()
        if self.stage_id.final_stage:
            self. write({'state':'rejected'})
            # self.kanban_state='blocked'
        pass
    def action_apply(self):
        self.ensure_one()
        
        data={'state':'done','kanban_state':'done'}
        last_stage=self.stage_find(self.id, [ ('final_stage', '=', True)])
        if last_stage:
            data['stage_id']=last_stage
        self.write(data)
        #Recalculate product's ECO Count
        self.product_tmpl_id.recalcul_eco_count()

    def action_see_attachments(self):
        pass 
    def open_new_bom(self):
        pass
    def _alias_get_creation_values(self):
        values = super(Eco, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('mrp.plm.eco.stage').id
        return values
    #     print('toto')
    def stage_find(self, type_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        type_ids = set()
        if type_id:
            type_ids.add(type_id)
        for eco in self:
            if eco.type_id:
                type_ids.add(eco.type_id.id)
        # eco_ids.extend(self.mapped('plm_id').ids)
        if type_ids:
            search_domain = [ ('type_ids', 'in', list(type_ids))]
        else:
            search_domain = [('type_ids', '=', False)]

        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        res=self.env['mrp.plm.eco.stage'].search(search_domain, order=order, limit=1)
        return res.id if res else False
        #return self.env['mrp.plm.eco.stage'].search(search_domain, order=order, limit=1).id

    def _read_group_stage_names(self, stages, domain, order):
        type_id = self.env.context.get(DEFAULT_TYPE_ID) or False

        #TO CHECK: why domain filter is not working 
        if not type_id:
            domain=[]
        domain=[]
        stages_ids=stages.search(domain,order=order)
        return stages_ids

    def _compute_allow_change_kanban_state(self):
        for record in self:
            record.allow_change_kanban_state=True