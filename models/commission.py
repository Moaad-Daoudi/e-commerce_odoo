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
    
    amount_commission = fields.Monetary(string="Commission Plateforme")
    amount_vendor = fields.Monetary(string="Montant Net Vendeur")
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'), # Commande facturée
        ('paid', 'Payé au vendeur'), # Inclus dans un Payout
        ('cancel', 'Annulé')
    ], default='draft', string="Statut")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('marketplace.commission') or 'New'
        return super(MarketplaceCommission, self).create(vals)