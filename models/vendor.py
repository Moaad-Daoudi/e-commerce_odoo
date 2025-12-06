# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MarketplaceVendor(models.Model):
    _name = 'marketplace.vendor'
    _description = 'Marketplace Vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'shop_name'

    partner_id = fields.Many2one('res.partner', string="User/Partner", required=True, readonly=True)
    shop_name = fields.Char(string="Shop Name", required=True)
    shop_url = fields.Char(string="Shop URL ID", required=True)
    phone = fields.Char(string="Business Phone")
    email = fields.Char(string="Business Email")
    description = fields.Text(string="Shop Description")
    
    # Store images
    image_1920 = fields.Image("Shop Banner", max_width=1920, max_height=500)
    image_128 = fields.Image("Shop Logo", max_width=128, max_height=128)

    state = fields.Selection([
        ('new', 'New Request'),
        ('active', 'Approved'),
        ('rejected', 'Rejected')
    ], default='new', string="Status", tracking=True)
    
    # Financial fields
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    default_commission_rate = fields.Float(string="Commission Rate (%)", default=10.0)
    balance = fields.Monetary(string="Balance", currency_field='currency_id', default=0.0)
    
    # Relations
    product_ids = fields.One2many('product.template', 'vendor_id', string="Products")
    commission_ids = fields.One2many('marketplace.commission', 'vendor_id', string="Commissions")

    _sql_constraints = [
        ('partner_uniq', 'unique(partner_id)', 'You already have a vendor profile!'),
        ('shop_url_uniq', 'unique(shop_url)', 'This Shop URL is already taken.')
    ]

    def action_approve(self):
        """ 
        1. Set state to Active 
        2. Add the user to the 'Vendor' security group (without changing their base access type)
        """
        for record in self:
            record.state = 'active'
            
            # Find the user associated with this partner
            user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)], limit=1)
            if user:
                # Add to Vendor Group (using sudo to bypass access rights)
                group_vendor = self.env.ref('marketplace_platform.group_marketplace_vendor')
                user.sudo().write({'groups_id': [(4, group_vendor.id)]})
                
                record.partner_id.sudo().write({'is_vendor': True})

    def action_reject(self):
        for record in self:
            record.state = 'rejected'