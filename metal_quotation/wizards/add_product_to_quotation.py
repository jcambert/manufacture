from odoo import api, exceptions, fields, models, _

class AddProductToQuotationWizard(models.TransientModel):
    _name='metal.add.product.to.quotation.wizard'
    _description='Add Product To Quotation Wizard'
    _inherit=['metal.quotation.mixin']

    name = fields.Char('Name',required=True,index=True,default=_('New Product'))
    description = fields.Text('Description')
    revision=fields.Char(string='Revision')
    quotation_id=fields.Many2one('metal.quotation',readonly=True,ondelete='cascade',string='Quotation',default=lambda self: self.env.context.get('default_quotation_id',False))
    def action_add_product(self):
        self.ensure_one()
        product=self.env['metal.quotation.product'].create({
            'name': self.name,
            'description': self.description,
            'revision': self.revision,
            'quotation_id': self.quotation_id.id,
            'material_margin': self.quotation_id.material_margin,
            'component_margin': self.quotation_id.component_margin,
            'be_time': self.quotation_id.be_time,
            'be_cost': self.quotation_id.be_cost,
            'fad_cost': self.quotation_id.fad_cost,
            'tool_cost': self.quotation_id.tool_cost,
            'st_margin': self.quotation_id.st_margin,
            'note': self.quotation_id.note,
        })

        prices=[]
        for price in self.quotation_id.prices_ids:
            prices.append({'product_id':product.id,'qty':price.qty,'margin':price.margin})

        self.env['metal.quotation.product.price'].create(prices)
        
        return {
            'name': 'view.product.action',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'metal.quotation.product',
            'res_id': product.id,
            'target': 'current',
            'context': {'default_quotation_id': self.quotation_id.id}
        }
        # return {'type': 'ir.actions.act_window_close'}

    