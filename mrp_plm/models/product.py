from odoo import api, fields, models
class ProductTemplate(models.Model):
    _inherit = "product.template"

    eco_ids = fields.One2many('mrp.plm.eco', 'product_tmpl_id', 'Ecos')
    eco_count = fields.Integer('# ECO',compute='_compute_eco_count', compute_sudo=False,readonly=True,store=True)
    eco_count_blocking = fields.Integer('# ECO Blocking',compute='_compute_eco_count', compute_sudo=False,readonly=True,store=True)
    
    
    def _compute_eco_count(self):
        for product in self:
            not_dones=product.eco_ids.filtered(lambda x:x.state not in ['done']) 
            product.eco_count = len(not_dones)
            product.eco_count_blocking =len( not_dones.filtered(lambda x: (x.sale_ok and not x.can_manufacture) and (x.purchase_ok and not x.can_purchase)))

    
    def recalcul_eco_count(self):
        self.ensure_one()
        not_dones=self.eco_ids.filtered(lambda x:x.state not in ['done']) 
        eco_count = len(not_dones)
        eco_count_blocking =len( not_dones.filtered(lambda x: (x.sale_ok and not x.can_manufacture) and (x.purchase_ok and not x.can_purchase)))
        self.write({'eco_count':eco_count,'eco_count_blocking':eco_count_blocking})