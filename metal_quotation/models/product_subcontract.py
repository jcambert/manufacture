from odoo import api, exceptions, fields, models, _

class QuotationProductSubcontract(models.Model):
    _name='metal.quotation.product.subcontract'
    _description='Product Subcontract'

    name = fields.Char('Name',required=True,index=True)
    cost = fields.Float('Subcontracting Cost')
    
    product_id = fields.Many2one('metal.quotation.product',string='Product',ondelete='cascade')
    quotation_price_id=fields.Many2one('metal.quotation.product.price',string='Quotation Price',ondelete='cascade')