# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class informeBatchm(models.Model):
    _name = 'informe.batchmin'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', store=True, compute='_compute_name')
    categ_id = fields.Many2one('product.category', string='Category')
    detalle_ids = fields.One2many('informe.batchmin.detalle', 'informe_bm_id', string="Detalles")
    ultima_actualizacion = fields.Datetime('Ultima actualización')

    @api.depends('categ_id')
    def _compute_name(self):
        nombrec = "."
        for record in self:
            if record.categ_id:
                nombrec = record.categ_id.display_name
                record.name = nombrec
            else:
                record.name = nombrec

    def calcular(self):
        self.ultima_actualizacion = datetime.datetime.now()
        for detalle in self.detalle_ids:
            detalle.unlink()
        sale_ids = self.env['stock.move'].search([
            ('route_ids', 'ilike', 'Manufac'),
            ('location_id', 'not ilike', 'virtual'),
            ('picking_type_id', 'ilike', 'Manufac'),
            ('categ_id', '=', self.categ_id.id),
            ('state', 'in', ['confirmed', 'partially_available', 'waiting']),
        ])
        product_ids = sale_ids.mapped('product_id')
        for product_id in product_ids:
            sale_filtrada_ids = sale_ids.filtered(lambda x: x.product_id == product_id)
            product_quantity_ids = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', product_id.product_tmpl_id.id),
            ])
            self.env['informe.batchmin.detalle'].create({
                'informe_bm_id': self.id,
                'default_code': product_id.default_code,
                'product_id': product_id.id,
                'product_name': product_id.display_name,
                'product_qty': sum(sale_filtrada_ids.mapped('product_uom_qty')),
                'cantidad_reservada': sum(sale_filtrada_ids.mapped('reserved_availability')),
                'batch_minimo': sum(product_quantity_ids.mapped('product_qty')),
            })

    def create_orderP(self):
        for record in self:
            for line in record.detalle_ids:
                if line.ready == True:
                    if line.cantidad_real < line.batch_minimo:
                        vals = {
                            'product_id': line.product_id.id,
                            'product_qty': line.batch_minimo,
                            'product_uom_id': line.product_id.uom_id.id,
                        }
                        self.env['mrp.production'].create(vals)
                    else:
                        vals = {
                            'product_id': line.product_id.id,
                            'product_qty': line.cantidad_real,
                            'product_uom_id': line.product_id.uom_id.id,
                        }
                        self.env['mrp.production'].create(vals)

class batchminDetalle(models.Model):
    _name = 'informe.batchmin.detalle'

    informe_bm_id = fields.Many2one('informe.batchmin', string='Informe batch minimo')
    product_id = fields.Many2one('product.product', string='Producto')
    product_qty = fields.Float('Cantidad demandada')
    cantidad_reservada = fields.Float('Cantidad reservada')
    cantidad_real = fields.Float('Cantidad real', store=True, compute='_compute_cantidad_real')
    diferencia = fields.Float('Diferencia', store=True, compute='_compute_diferencia')
    batch_minimo = fields.Float('Batch minimo')
    n_batch = fields.Float('N° Batch', compute='_compute_n_batch')
    product_name = fields.Char('Nombre producto')
    default_code = fields.Char('Codigo')
    ready = fields.Boolean('Ready')

    @api.depends('product_qty', 'cantidad_reservada')
    def _compute_cantidad_real(self):
        for record in self:
            record.cantidad_real = record.product_qty - record.cantidad_reservada

    @api.depends('cantidad_real', 'batch_minimo')
    def _compute_diferencia(self):
        for record in self:
            record.diferencia = record.batch_minimo - record.cantidad_real

    @api.depends('cantidad_real', 'batch_minimo')
    def _compute_n_batch(self):
        for record in self:
            if record.cantidad_real and record.batch_minimo:
                record.n_batch = record.cantidad_real / record.batch_minimo
            else:
                record.n_batch = 0.0

class bomProduct(models.Model):
    _inherit = 'stock.move'

    route_ids = fields.Many2many('stock.location.route', string='Rutas', related='product_id.route_ids')
    categ_id = fields.Many2one('product.category', string='Category', related='product_id.categ_id')
