from odoo import models, fields, api

class moq_psi(models.Model):
    _inherit="product.supplierinfo"

    omc = fields.Float(string="MOQ", help="Cantidad Mínima en la orden")
