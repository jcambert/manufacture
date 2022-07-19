from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from odoo.osv import expression

class EcoProduction(models.Model):
    """ Manufacturing Orders """
    
    _inherit = ['mrp.production']
    has_plm = fields.Boolean(string='Has PLM', compute='_compute_has_plm',search='_search_plm')
    plm_count=fields.Integer(string='PLM Count',compute='_compute_has_plm')
    plm_badge = fields.Char(string='PLM', compute='_compute_has_plm')

    @api.depends('product_id', 'product_tmpl_id')
    def _compute_has_plm(self):
        for production in self:
            production.has_plm = production.product_tmpl_id.eco_count_blocking>0
            production.plm_count = production.product_tmpl_id.eco_count_blocking
            production.plm_badge = "%s eco" % production.plm_count 

    def action_view_eco(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("mrp_plm.mrp_eco_product_action")
        action['context'] = literal_eval(action.get('context'))
        
        if self and len(self) == 1:
            action['context'].update({
                'default_product_tmpl_id': self.product_tmpl_id.id,
                'search_default_product_tmpl_id': self.product_tmpl_id.id
            })
        else:
            action['domain'] = expression.AND([action.get('domain', []), [('product_tmpl_id', 'in', self.ids)]])
        return action

    def _search_plm(self, operator, value):
        recs = self.search([]).filtered(lambda x : x.has_plm)
        if recs:
            return [('id', 'in', [x.id for x in recs])]
        else:
            return [('id', '=', False)]

    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. @see mrp.production"""
        self=self.filtered(lambda x: not x.has_plm)
        res=super(EcoProduction,self).button_plan()
        return res