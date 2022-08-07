from odoo import api, models
class QuotationReport(models.AbstractModel):
    _name='report.metal_quotation.quotation_report'
    _description= 'Quotation Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs=self.env['metal.quotation'].browse(docids)
        return {'doc_ids': docids, 'doc_model': 'metal.quotation', 'data': data,'docs':docs}