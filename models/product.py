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
    
    def action_submit_for_approval(self):
        """Vendor submits product for admin approval"""
        for product in self:
            product.write({
                'approval_state': 'pending',
                'is_published': False  # Unpublish until approved
            })
    
    def action_approve_product(self):
        """Admin approves the product"""
        for product in self:
            product.write({
                'approval_state': 'approved',
                'is_published': True  # Publish to website
            })
            # Send notification to vendor
            if product.vendor_id:
                product.message_post(
                    body=f"Your product '{product.name}' has been approved and is now live!",
                    subject="Product Approved",
                    partner_ids=[product.vendor_id.partner_id.id]
                )
    
    def action_reject_product(self):
        """Admin rejects the product"""
        for product in self:
            product.write({
                'approval_state': 'rejected',
                'is_published': False
            })
            # Send notification to vendor
            if product.vendor_id:
                product.message_post(
                    body=f"Your product '{product.name}' has been rejected. Please review and resubmit.",
                    subject="Product Rejected",
                    partner_ids=[product.vendor_id.partner_id.id]
                )