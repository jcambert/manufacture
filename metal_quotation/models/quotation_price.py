from odoo import api, exceptions, fields, models, _

class QuotationPrice(models.Model):
    _name = 'metal.quotation.price'
    _description = 'Quotation Price'
    _inherit=['metal.quotation.price.mixin']
    _order = 'qty desc'
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