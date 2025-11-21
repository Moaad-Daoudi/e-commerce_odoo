# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class MarketplacePayout(models.Model):
    _name = 'marketplace.payout'
    _description = 'Demande de Versement Vendeur'
    _inherit = ['mail.thread']

    name = fields.Char(string="Référence", default="New", readonly=True)
    vendor_id = fields.Many2one('marketplace.vendor', string="Vendeur", required=True)
    
    currency_id = fields.Many2one('res.currency', related='vendor_id.currency_id')
    amount = fields.Monetary(string="Montant Demandé", required=True)
    
    request_date = fields.Date(string="Date de demande", default=fields.Date.today)
    payment_date = fields.Date(string="Date de paiement")
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('requested', 'Demandé'),
        ('validated', 'Validé'),
        ('paid', 'Payé'),
        ('rejected', 'Rejeté')
    ], default='draft', tracking=True)
    
    payment_reference = fields.Char(string="Référence Bancaire/Transaction")

    def action_request(self):
        # Vérifier si le solde est suffisant avant de demander
        if self.amount > self.vendor_id.balance:
            raise models.ValidationError(_("Solde insuffisant pour cette demande."))
        self.state = 'requested'