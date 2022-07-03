from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from odoo.osv import expression

class EcoProduction(models.Model):
    """ Manufacturing Orders """
    
    _inherit = ['mrp.production']
    has_plm = fields.Boolean(string='Has PLM', compute='_compute_has_plm')
    plm_count=fields.Integer(string='PLM Count',compute='_compute_has_plm')

    @api.depends('product_id', 'product_tmpl_id')
    def _compute_has_plm(self):
        for production in self:
            production.has_plm = production.product_tmpl_id.eco_count>0
            production.plm_count = production.product_tmpl_id.eco_count
    def action_view_eco(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("mrp_plm.mrp_eco_product_action")
        action['context'] = literal_eval(action.get('context'))
        
        if self and len(self) == 1:
            action['context'].update({
                'default_product_tmpl_id': self.ids[0],
                'search_default_product_tmpl_id': self.ids[0]
            })
        else:
            action['domain'] = expression.AND([action.get('domain', []), [('product_tmpl_id', 'in', self.ids)]])
        return action