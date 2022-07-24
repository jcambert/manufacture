from email.policy import default
from odoo import api, exceptions, fields, models, _

class MrpWorkcenter(models.Model):
    _inherit = ['mrp.workcenter']

    method=fields.Selection([('manual','Manual'),('cadence','Cadence')],string='Method',default='manual')
    base_temps=fields.Float(string='Base Temps', default=0.0)
    base_temps_uom=fields.Float(string='Base Temps Horaire', default=0.0)
    calculated=fields.Boolean(string='Calculated', default=False)
    center_type=fields.Selection([('standard','Standard') ,('laser','Laser'),('punch','Punching')],string='Center Type',default='standard')
    laser_params_ids=fields.One2many('mrp.workcenter.cutting.speed','workcenter_id',string='Cutting Speeds')
    laser_params_count=fields.Integer(string='Cutting Speeds Count', compute='_compute_laser_params_count')

    @api.depends('laser_params_ids')
    def _compute_laser_params_count(self):
        for record in self:
            record.laser_params_count = len(record.laser_params_ids)

class MrpCuttingSpeed(models.Model):
    _name='mrp.workcenter.cutting.speed'
    _description='Workcenter whith cutting speed'
    _inherit=[]
    _order='workcenter_id,material_id,gas,thickness'
    workcenter_id=fields.Many2one('mrp.workcenter',string='Workcenter',domain="[('center_type','=','laser')]")
    thickness=fields.Float(string='Thickness',required=True)
    speed_ext=fields.Integer(string='External Speed',help="meter per minute",required=True)
    speed_int=fields.Integer(string='Internal Speed',help="meter per minute",required=True)
    material_id=fields.Many2one('metal.material',string='Material',required=True)
    gas=fields.Selection([('oxygen','O2'),('azote','NA')],string='Gas',default='oxygen',required=True)