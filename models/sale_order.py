# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_marketplace_order = fields.Boolean(string="Commande Marketplace", compute='_compute_is_marketplace', store=True)
    
    @api.depends('order_line.vendor_id')
    def _compute_is_marketplace(self):
        for order in self:
            order.is_marketplace_order = any(order.order_line.mapped('vendor_id'))

    def action_confirm(self):
        """ Surcharge de la confirmation pour générer les commissions """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.is_marketplace_order:
                order._create_marketplace_commissions()
                # Optionnel : Déclencher le Split Order ici
        return res

    def _create_marketplace_commissions(self):
        """ Génère les enregistrements de commission pour chaque ligne """
        Commission = self.env['marketplace.commission']
        for line in self.order_line:
            if line.vendor_id:
                # Calcul des montants
                rate = line.product_id.commission_rate or line.vendor_id.default_commission_rate
                comm_amount = line.price_subtotal * (rate / 100.0)
                vendor_amount = line.price_subtotal - comm_amount

                Commission.create({
                    'vendor_id': line.vendor_id.id,
                    'order_line_id': line.id,
                    'amount_commission': comm_amount,
                    'amount_vendor': vendor_amount,
                    'currency_id': line.currency_id.id,
                    'state': 'draft', # Sera confirmé lors du paiement/facturation
                })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vendor_id = fields.Many2one(
        'marketplace.vendor', 
        related='product_id.product_tmpl_id.vendor_id', 
        string="Vendeur", 
        store=True,
        readonly=True
    )