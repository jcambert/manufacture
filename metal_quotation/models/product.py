from odoo import api, exceptions, fields, models, _

class QuotationProduct(models.Model):
    _name="metal.quotation.product"
    _description="Quotation Product"
    _order = "name, id"
    _inherit=['we.archive.mixin','we.company.currency.mixin','we.color.mixin']

    name=fields.Char(string='Name', required=True,index=True)
    description = fields.Char('Description')
    revision=fields.Char(string='Revision')
    quotation_id=fields.Many2one('metal.quotation',ondelete='cascade',string='Quotation')
    