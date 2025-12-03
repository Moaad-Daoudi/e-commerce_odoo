# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class MarketplaceController(http.Controller):
    
    # Home Page for guest
    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):

        # Example data loading
        categories = request.env['product.category'].sudo().search([], limit=6)
        products   = request.env['product.template'].sudo().search([], limit=8)
        vendors    = request.env['marketplace.vendor'].sudo().search([], limit=4)

        return request.render('marketplace_platform.home_page', {
            'categories': categories,
            'products': products,
            'vendors': vendors
        })

    @http.route(['/my/marketplace'], type='http', auth="user", website=True)
    def vendor_dashboard(self, **kw):
        # Récupérer le vendeur lié à l'utilisateur connecté
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor:
            return request.redirect('/marketplace/register')
            
        values = {
            'vendor': vendor,
            'orders': request.env['sale.order'].search([('order_line.vendor_id', '=', vendor.id)]),
        }
        # Retourne le template QWeb (à créer dans les views)
        return request.render("marketplace_platform.portal_vendor_dashboard", values)

    @http.route(['/marketplace/register'], type='http', auth="user", website=True)
    def vendor_registration(self, **post):
        if request.httprequest.method == 'POST':
            # Création simple du vendeur
            vals = {
                'shop_name': post.get('shop_name'),
                'shop_url': post.get('shop_url'),
                'partner_id': request.env.user.partner_id.id,
                'state': 'new',
            }
            request.env['marketplace.vendor'].create(vals)
            return request.redirect('/my/marketplace?msg=pending')
            
        return request.render("marketplace_platform.vendor_registration_form")