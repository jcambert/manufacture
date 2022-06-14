from odoo import api, fields, models
class ProductTemplate(models.Model):
    _inherit = "product.template"

    eco_ids = fields.One2many('mrp.plm.eco', 'product_tmpl_id', 'Ecos')
    eco_count = fields.Integer('# ECO',compute='_compute_eco_count', compute_sudo=False)

    def _compute_eco_count(self):
        for product in self:
            product.eco_count = self.env['mrp.plm.eco'].search_count([('product_tmpl_id', '=', product.id)])

        