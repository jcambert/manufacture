# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class EcoRoutingChange(models.Model):
    _name='mrp.plm.eco.routing.change'
    _description='Eco Routing Change'
    
    change_type=fields.Selection([('add','Add'),('remove','Remove'),('update','Update')],string='Change Type',required=True)
    eco_id=fields.Many2one('mrp.plm.eco',ondelete='restrict',string="ECO")
    new_time_cycle_manual=fields.Float('New Time Cycle (Manual)')
    old_time_cycle_manual=fields.Float('Old Time Cycle (Manual)')
    operation_id=fields.Many2one('mrp.routing.workcenter',ondelete='restrict',string="Operation")
    operation_name=fields.Char('Operation Name',related='operation_id.name')
    upd_time_cycle_manual=fields.Float('New Time Cycle (Manual)',store=True,compute='_compute_upd_time_cycle_manual')
    workcenter_id=fields.Many2one('mrp.workcenter',ondelete='restrict',string="Workcenter")
    
    @api.depends('new_time_cycle_manual','old_time_cycle_manual')
    def _compute_upd_time_cycle_manual(self):
        for record in self:
            if record.new_time_cycle_manual:
                record.upd_time_cycle_manual=record.new_time_cycle_manual
            else:
                record.upd_time_cycle_manual=record.old_time_cycle_manual