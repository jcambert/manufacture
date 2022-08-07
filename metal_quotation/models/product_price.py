from cv2 import QT_STYLE_ITALIC
from odoo import api, exceptions, fields, models, _

class QuotationProductPrice(models.Model):
    _name='metal.quotation.product.price'
    _description='Quotation Product Price'
    _inherit=['metal.quotation.price.mixin']

    # qty=fields.Integer('Qty')
    # margin=fields.Float('Margin',digits=(6,2))
    # price=fields.Float('Price',digits=(6,2),compute='_compute_price',store=True,compute_sudo=True)

    subcontract_ids=fields.One2many('metal.quotation.product.subcontract','quotation_price_id',string='Subcontracts')
    product_id = fields.Many2one('metal.quotation.product',string='Product',required=True,ondelete='cascade')
    total_subcontracting_cost=fields.Float('Total Subcontracting Cost',compute='_compute_total_subcontracting_cost',store=True,compute_sudo=True)

    @api.depends('subcontract_ids','subcontract_ids.cost')
    def _compute_total_subcontracting_cost(self):
        for record in self:
             record.total_subcontracting_cost=sum(record.subcontract_ids.mapped('cost'))
        return True
    @api.depends('qty','margin','subcontract_ids','product_id','product_id.total_subcontracting_cost','product_id.total_preparation_cost','product_id.total_operation_cost','product_id.total_component_cost')
    def _compute_price(self):
        for record in self:
            total_subcontracting_cost = record.total_subcontracting_cost
            total_preparation_cost=record.product_id.total_preparation_cost
            total_operation_cost=record.product_id.total_operation_cost
            total_component_cost=record.product_id.total_component_cost

            component_margin=record.product_id.component_margin
            st_margin=record.product_id.st_margin

            # price=total_component_cost * (1+component_margin/100) 
            # price+=(total_subcontracting_cost) * (1+st_margin/100)
            # price+=(total_preparation_cost/record.qty)
            # price+=total_operation_cost

            # record.price = price * (1+record.margin/100)
            record.price = self.compute_price(record.qty,record.margin,total_subcontracting_cost,total_preparation_cost,total_operation_cost,total_component_cost,component_margin,st_margin)
        return True