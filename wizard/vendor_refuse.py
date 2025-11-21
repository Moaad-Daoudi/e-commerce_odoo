# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MarketplaceVendorRefuse(models.TransientModel):
    _name = 'marketplace.vendor.refuse'
    _description = 'Refuser un vendeur'

    vendor_id = fields.Many2one('marketplace.vendor', string="Vendeur", required=True)
    reason = fields.Text(string="Motif du refus", required=True)

    def action_refuse_reason(self):
        self.ensure_one()
        # Changer l'état du vendeur
        self.vendor_id.state = 'suspended'
        self.vendor_id.message_post(body=f"Vendeur refusé/suspendu. Motif : {self.reason}")
        return {'type': 'ir.actions.act_window_close'}
