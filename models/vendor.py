# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MarketplaceVendor(models.Model):
    _name = 'marketplace.vendor'
    _description = 'Vendeur Marketplace'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Pour le chatter et le suivi
    _rec_name = 'shop_name'

    partner_id = fields.Many2one(
        'res.partner', 
        string="Partenaire Associé", 
        required=True, 
        ondelete='cascade'
    )
    
    shop_name = fields.Char(string="Nom de la Boutique", required=True, tracking=True)
    shop_url = fields.Char(string="URL de la Boutique", required=True)
    
    state = fields.Selection([
        ('new', 'Nouveau'),
        ('pending', 'En Attente'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu')
    ], string="Statut", default='new', tracking=True)

    default_commission_rate = fields.Float(
        string="Commission par Défaut (%)", 
        default=10.0,
        help="Pourcentage prélevé par la plateforme sur les ventes de ce vendeur."
    )

    # Gestion Financière
    currency_id = fields.Many2one('res.currency', related='partner_id.currency_id')
    balance = fields.Monetary(
        string="Solde Disponible", 
        compute='_compute_balance', 
        store=True
    )
    
    commission_ids = fields.One2many('marketplace.commission', 'vendor_id', string="Commissions")
    product_ids = fields.One2many('product.template', 'vendor_id', string="Produits")

    _sql_constraints = [
        ('shop_url_unique', 'unique(shop_url)', 'L\'URL de la boutique doit être unique !')
    ]

    @api.depends('commission_ids.state', 'commission_ids.amount_vendor')
    def _compute_balance(self):
        """ Calcule le solde en fonction des commissions confirmées """
        for record in self:
            # Logique simplifiée : somme des montants vendeurs confirmés moins les paiements déjà effectués
            # À affiner avec le modèle Payout
            income = sum(record.commission_ids.filtered(lambda c: c.state == 'confirmed').mapped('amount_vendor'))
            record.balance = income 
            # Note: Il faudrait soustraire les 'marketplace.payout' payés ici.

    def action_approve_vendor(self):
        self.state = 'active'
        # Créer automatiquement les accès portail ici si nécessaire