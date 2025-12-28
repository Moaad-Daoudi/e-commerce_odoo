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
    
    # Social Media Fields
    social_facebook = fields.Char(string="Facebook")
    social_twitter = fields.Char(string="X (Twitter)")
    social_instagram = fields.Char(string="Instagram")
    
    # Store Location (linking to partner fields for simplicity)
    street = fields.Char(related='partner_id.street', readonly=False)
    city = fields.Char(related='partner_id.city', readonly=False)
    zip = fields.Char(related='partner_id.zip', readonly=False)
    country_id = fields.Many2one(related='partner_id.country_id', readonly=False)

    state = fields.Selection([
        ('new', 'New Request'),
        ('active', 'Approved'),
        ('rejected', 'Rejected')
    ], default='new', string="Status", tracking=True)
    
    # Financial fields
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    default_commission_rate = fields.Float(string="Commission Rate (%)", default=10.0)
    balance = fields.Monetary(string="Balance", currency_field='currency_id', compute='_compute_balance', store=True)
    
    # Relations
    product_ids = fields.One2many('product.template', 'vendor_id', string="Products")
    commission_ids = fields.One2many('marketplace.commission', 'vendor_id', string="Commissions")
    
    # store=True est OBLIGATOIRE pour pouvoir trier dessus dans le contrôleur (order='sale_count desc')
    sale_count = fields.Integer(string="Ventes Totales", compute='_compute_kpi', store=True)
    total_commission = fields.Monetary(string="Total Commissions", compute='_compute_kpi', currency_field='currency_id', store=True)

    _sql_constraints = [
        ('partner_uniq', 'unique(partner_id)', 'You already have a vendor profile!'),
        ('shop_url_uniq', 'unique(shop_url)', 'This Shop URL is already taken.')
    ]

    @api.depends('commission_ids', 'commission_ids.state', 'commission_ids.amount_vendor')
    def _compute_balance(self):
        """Calculate available balance from confirmed commissions minus paid ones"""
        for rec in self:
            confirmed_comms = rec.commission_ids.filtered(lambda c: c.state in ['confirmed', 'paid'])
            paid_comms = rec.commission_ids.filtered(lambda c: c.state == 'paid')
            
            total_earned = sum(confirmed_comms.mapped('amount_vendor'))
            total_paid = sum(paid_comms.mapped('amount_vendor'))
            rec.balance = total_earned - total_paid

    @api.depends('commission_ids', 'commission_ids.state')
    def _compute_kpi(self):
        for rec in self:
            # On compte les ventes confirmées (via les commissions générées)
            confirmed_comms = rec.commission_ids.filtered(lambda c: c.state in ['confirmed', 'paid'])
            rec.sale_count = len(confirmed_comms)
            rec.total_commission = sum(confirmed_comms.mapped('amount_commission'))

    def action_approve(self):
        """ 
        1. Set state to Active 
        2. Add the user to the 'Vendor' security group
        """
        for record in self:
            record.state = 'active'
            
            # Find the user associated with this partner
            user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)], limit=1)
            if user:
                # Add to Vendor Group (using sudo to bypass access rights)
                # Note: Assurez-vous que l'ID XML 'group_marketplace_vendor' est correct dans votre security.xml
                group_vendor = self.env.ref('marketplace_platform.group_marketplace_vendor', raise_if_not_found=False)
                if group_vendor:
                    user.sudo().write({'groups_id': [(4, group_vendor.id)]})
                
                record.partner_id.sudo().write({'is_vendor': True})

    def action_reject(self):
        for record in self:
            record.state = 'rejected'