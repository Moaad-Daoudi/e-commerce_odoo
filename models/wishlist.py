# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductWishlist(models.Model):
    _name = 'product.wishlist'
    _description = 'Product Wishlist'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    website_id = fields.Many2one('website', string='Website', ondelete='cascade')
    
    # Related fields for easy access
    product_name = fields.Char(related='product_id.name', string='Product Name', readonly=True)
    product_price = fields.Float(related='product_id.list_price', string='Price', readonly=True)
    product_image = fields.Image(related='product_id.image_1920', string='Product Image', readonly=True)
    
    create_date = fields.Datetime(string='Added On', readonly=True)
    
    _sql_constraints = [
        ('unique_partner_product', 'unique(partner_id, product_id, website_id)', 
         'This product is already in your wishlist!')
    ]
    
    @api.model
    def _add_to_wishlist(self, partner_id, product_id, website_id=None):
        """Helper method to add product to wishlist"""
        vals = {
            'partner_id': partner_id,
            'product_id': product_id,
        }
        if website_id:
            vals['website_id'] = website_id
            
        # Check if already exists
        existing = self.search([
            ('partner_id', '=', partner_id),
            ('product_id', '=', product_id),
            ('website_id', '=', website_id if website_id else False)
        ], limit=1)
        
        if existing:
            return existing
        
        return self.create(vals)
