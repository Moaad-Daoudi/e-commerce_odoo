# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_vendor = fields.Boolean(
        string="Est un vendeur",
        help="Cochez cette case si ce contact est un vendeur sur la marketplace."
    )
    
    vendor_profile_id = fields.Many2one(
        'marketplace.vendor',
        string="Profil Vendeur",
        readonly=True,
        help="Lien vers le profil vendeur associé."
    )