# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vendor_id = fields.Many2one(
        'marketplace.vendor', 
        string="Vendeur", 
        help="Vendeur propriétaire de ce produit",
        index=True
    )
    
    approval_state = fields.Selection([
        ('draft', 'Brouillon'),
        ('pending', 'En attente d\'approbation'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté')
    ], string="Statut d'approbation", default='draft', tracking=True)

    commission_rate = fields.Float(
        string="Taux de Commission Spécifique (%)",
        help="Laisser à 0.0 pour utiliser le taux par défaut du vendeur."
    )

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        if self.vendor_id:
            self.commission_rate = self.vendor_id.default_commission_rate