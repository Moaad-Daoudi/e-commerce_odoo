# -*- coding: utf-8 -*-
from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vendor_id = fields.Many2one(
        'marketplace.vendor', 
        string="Vendeur", 
        help="Vendeur responsable de cette livraison (si Dropshipping ou Split)",
        index=True
    )

class AccountMove(models.Model):
    _inherit = 'account.move'

    vendor_id = fields.Many2one(
        'marketplace.vendor',
        string="Vendeur",
        help="Utilisé pour filtrer les factures par vendeur dans le portail."
    )