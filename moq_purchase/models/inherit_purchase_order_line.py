# -*- coding: utf-8 -*-

from odoo import models, fields, api

class moq_pol(models.Model):
    _inherit="purchase.order.line"

    umc = fields.Float(string="MOQ",compute="_compute_moq", help="Establece la unidad mínima de compra del proveedor.")

    def _compute_moq(self):
        for rec in self:
            seller_id = rec.product_id.seller_ids.filtered(lambda s: s.name.id == rec.order_id.partner_id.id)
            rec.umc = seller_id.omc if seller_id else 0.0

