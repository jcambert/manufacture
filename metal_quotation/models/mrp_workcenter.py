from odoo import api, exceptions, fields, models, _

class MrpWorkcenter(models.Model):
    _inherit = ['mrp.workcenter']

    method=fields.Selection([('manuel','Manual'),('cadence','Cadence')],string='Method',default='manual')
    base_temps=fields.Float(string='Base Temps', default=0.0)
    base_temps_uom=fields.Float(string='Base Temps Horaire', default=0.0)
    calculated=fields.Boolean(string='Calculated', default=False)