# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MarketplaceCommission(models.Model):
    _name = 'marketplace.commission'
    _description = 'Commission Marketplace'
    _order = 'create_date desc'

    name = fields.Char(string="Référence", default="New", readonly=True)
    
    vendor_id = fields.Many2one('marketplace.vendor', string="Vendeur", required=True)
    order_line_id = fields.Many2one('sale.order.line', string="Ligne de commande", required=True)
    
    currency_id = fields.Many2one('res.currency', related='order_line_id.currency_id')
    
    # Total sale amount for this line
    sale_amount = fields.Monetary(string="Montant Total Vente", compute='_compute_amounts', store=True)
    
    # Commission taken by platform
    amount_commission = fields.Monetary(string="Commission Plateforme", compute='_compute_amounts', store=True)
    
    # Amount that goes to vendor (after commission)
    amount_vendor = fields.Monetary(string="Montant Net Vendeur", compute='_compute_amounts', store=True)
    vendor_amount = fields.Monetary(string="Montant Net Vendeur (alias)", compute='_compute_amounts', store=True)
    
    commission_rate = fields.Float(string="Taux Commission (%)", default=10.0)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'), # Commande facturée
        ('paid', 'Payé au vendeur'), # Inclus dans un Payout
        ('cancel', 'Annulé')
    ], default='draft', string="Statut")

    @api.depends('order_line_id.price_subtotal', 'commission_rate')
    def _compute_amounts(self):
        for record in self:
            if record.order_line_id:
                record.sale_amount = record.order_line_id.price_subtotal
                record.amount_commission = record.sale_amount * (record.commission_rate / 100.0)
                record.amount_vendor = record.sale_amount - record.amount_commission
                record.vendor_amount = record.amount_vendor
            else:
                record.sale_amount = 0.0
                record.amount_commission = 0.0
                record.amount_vendor = 0.0
                record.vendor_amount = 0.0

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('marketplace.commission') or 'New'
        return super(MarketplaceCommission, self).create(vals)