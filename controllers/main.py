# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import math

class MarketplaceController(http.Controller):
    
    # Home Page for guest
    @http.route(['/', '/page/<int:page>'], type='http', auth='public', website=True)
    def homepage(self, page=1, **kwargs):
        # Configuration
        items_per_page = 10
        domain = [('is_published', '=', True)]
        
        # Calculate Offset (Skip previous pages' items)
        offset = (page - 1) * items_per_page
        
        # Fetch Data
        ProductTemplate = request.env['product.template'].sudo()
        
        # Get total count to calculate total pages
        total_products = ProductTemplate.search_count(domain)
        
        # Get specific slice of products for this page
        products = ProductTemplate.search(
            domain, 
            limit=items_per_page, 
            offset=offset,
            order='website_sequence asc, create_date desc'
        )
        
        # fetch categories (keep existing logic)
        categories = request.env['product.public.category'].sudo().search([], limit=5)

        # 4. Pagination Data Calculation
        total_pages = math.ceil(total_products / items_per_page)
        
        # Generate page numbers list (e.g., [1, 2, 3, 4, 5])
        # Simple logic: show all. For complex logic (1 ... 5 6 7 ... 10), extra python logic is needed.
        page_range = range(1, total_pages + 1)

        return request.render('marketplace_platform.home_page', {
            'categories': categories,
            'products': products,
            # Pagination Data
            'pager': {
                'current_page': page,
                'total_pages': total_pages,
                'pages': page_range,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_num': page + 1,
                'prev_num': page - 1,
            }
        })
    
    # ALL CATEGORIES PAGE
    @http.route(['/categories', '/categories/page/<int:page>'], type='http', auth='public', website=True)
    def all_categories_view(self, page=1, search=None, **kw):
        # Configuration
        items_per_page = 12
        
        # Base domain
        domain = []
        if search:
            domain.append(('name', 'ilike', search))
        
        # Fetch categories with pagination
        Category = request.env['product.public.category'].sudo()
        total_categories = Category.search_count(domain)
        offset = (page - 1) * items_per_page
        total_pages = math.ceil(total_categories / items_per_page) if total_categories > 0 else 1
        
        categories = Category.search(domain, limit=items_per_page, offset=offset, order='name asc')
        
        # Get product count for each category
        category_data = []
        for cat in categories:
            product_count = request.env['product.template'].sudo().search_count([
                ('is_published', '=', True),
                ('public_categ_ids', 'child_of', cat.id)
            ])
            category_data.append({
                'category': cat,
                'product_count': product_count
            })
        
        page_range = range(1, total_pages + 1) if total_pages > 0 else range(1, 2)
        
        return request.render('marketplace_platform.all_categories_page', {
            'category_data': category_data,
            'search_term': search,
            'pager': {
                'current_page': page,
                'total_pages': total_pages,
                'pages': page_range,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_num': page + 1,
                'prev_num': page - 1,
            }
        })
        
    # CATEGORY ROUTE
    @http.route(['/category/<model("product.public.category"):category>',
                 '/category/<model("product.public.category"):category>/page/<int:page>'], 
                type='http', auth="public", website=True)
    def aura_category_view(self, category, page=1, search=None, min_price=None, max_price=None, vendor=None, sort=None, **kw):
        
        #  Base Configuration
        items_per_page = 10
        domain = [
            ('is_published', '=', True),
            ('public_categ_ids', 'child_of', category.id)
        ]

        # Apply Search Filter
        if search:
            domain.append(('name', 'ilike', search))

        # Apply Filters (if present in URL)
        if min_price:
            domain.append(('list_price', '>=', float(min_price)))
        if max_price:
            domain.append(('list_price', '<=', float(max_price)))
        if vendor:
            # Assumes 'vendor' param is the ID
            domain.append(('vendor_id', '=', int(vendor)))

        # Determine Sort Order
        order = 'website_sequence asc, create_date desc'  # Default
        if sort == 'price_asc':
            order = 'list_price asc'
        elif sort == 'price_desc':
            order = 'list_price desc'
        elif sort == 'name_asc':
            order = 'name asc'
        elif sort == 'newest':
            order = 'create_date desc'
        elif sort == 'popular':
            order = 'website_sequence asc'

        # Calculate Pagination
        ProductTemplate = request.env['product.template'].sudo()
        total_products = ProductTemplate.search_count(domain)
        offset = (page - 1) * items_per_page
        total_pages = math.ceil(total_products / items_per_page) if total_products > 0 else 1
        
        # Fetch Products
        products = ProductTemplate.search(
            domain, 
            limit=items_per_page, 
            offset=offset, 
            order=order
        )

        # Fetch Sidebar Data (Vendors available in this category)
        # We find vendors who actually have products in this category to show in filter
        all_products_in_cat = ProductTemplate.search([('public_categ_ids', 'child_of', category.id)])
        available_vendors = all_products_in_cat.mapped('vendor_id')

        # Pagination Range
        page_range = range(1, total_pages + 1) if total_pages > 0 else range(1, 2)
        
        # Pass current params to keep filters alive during pagination
        filter_params = []
        if search:
            filter_params.append('search=%s' % search)
        if min_price:
            filter_params.append('min_price=%s' % min_price)
        if max_price:
            filter_params.append('max_price=%s' % max_price)
        if vendor:
            filter_params.append('vendor=%s' % vendor)
        if sort:
            filter_params.append('sort=%s' % sort)
        
        keep_query = '&'.join(filter_params)

        return request.render("marketplace_platform.placeholder_category_page", {
            'category': category,
            'products': products,
            'vendors': available_vendors,
            'pager': {
                'current_page': page,
                'total_pages': total_pages,
                'pages': page_range,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_num': page + 1,
                'prev_num': page - 1,
                'keep_query': keep_query
            },
            'filters': {
                'search': search,
                'min_price': min_price,
                'max_price': max_price,
                'vendor': int(vendor) if vendor else None,
                'sort': sort
            }
        })
        
    # PRODUCT ROUTE
    @http.route('/product/<model("product.template"):product>', type='http', auth="public", website=True)
    def aura_product_view(self, product, **kw):
        # Fetch Related Products
        # Logic: Same category, excluding current product
        domain = [
            ('is_published', '=', True),
            ('public_categ_ids', 'in', product.public_categ_ids.ids),
            ('id', '!=', product.id)
        ]
        related_products = request.env['product.template'].sudo().search(domain, limit=4)
        
        # Fetch Categories (for 'Shop by Vibe' section)
        categories = request.env['product.public.category'].sudo().search([], limit=4)
        
        # Get vendor with sudo to bypass access restrictions
        vendor = product.vendor_id.sudo() if product.vendor_id else None
        vendor_partner = vendor.partner_id if vendor else None

        return request.render("marketplace_platform.placeholder_product_page", {
            'product': product,
            'vendor': vendor,
            'vendor_partner': vendor_partner,
            'related_products': related_products,
            'categories': categories,
        })
        
    # VENDOR PROFILE ROUTE
    @http.route(['/vendor/<model("marketplace.vendor"):vendor>',
                 '/vendor/<model("marketplace.vendor"):vendor>/page/<int:page>'], 
                type='http', auth="public", website=True)
    def aura_vendor_view(self, vendor, page=1, **kw):
        
        # Config
        items_per_page = 10
        domain = [
            ('is_published', '=', True),
            ('vendor_id', '=', vendor.id) # Filter by this vendor
        ]

        # Pagination
        ProductTemplate = request.env['product.template'].sudo()
        total_products = ProductTemplate.search_count(domain)
        offset = (page - 1) * items_per_page
        total_pages = math.ceil(total_products / items_per_page)
        
        # Fetch Products
        products = ProductTemplate.search(
            domain, 
            limit=items_per_page, 
            offset=offset, 
            order='list_price asc'
        )

        # Pager Data
        page_range = range(1, total_pages + 1)
        
        # Get vendor with sudo to bypass access restrictions
        vendor_sudo = vendor.sudo()
        vendor_partner = vendor_sudo.partner_id if vendor_sudo else None

        return request.render("marketplace_platform.vendor_profile_page", {
            'vendor': vendor_sudo,
            'vendor_partner': vendor_partner,
            'products': products,
            'pager': {
                'current_page': page,
                'total_pages': total_pages,
                'pages': page_range,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_num': page + 1,
                'prev_num': page - 1,
            }
        })
        
    # SEARCH RESULTS ROUTE
    @http.route(['/search', 
                 '/search/page/<int:page>'], 
                type='http', auth="public", website=True)
    def aura_search_view(self, page=1, search=None, min_price=None, max_price=None, vendor=None, category=None, sort=None, **kw):
        
        # 1. Base Domain (Published products only)
        domain = [('is_published', '=', True)]
        
        # 2. Apply Text Search (Name or Description)
        if search:
            domain += ['|', ('name', 'ilike', search), ('description_sale', 'ilike', search)]

        # 3. Apply Filters
        if min_price:
            domain.append(('list_price', '>=', float(min_price)))
        if max_price:
            domain.append(('list_price', '<=', float(max_price)))
        if vendor:
            domain.append(('vendor_id', '=', int(vendor)))
        if category:
            domain.append(('public_categ_ids', 'in', [int(category)]))

        # 4. Sort Order
        order = 'website_sequence asc, create_date desc' # Default
        if sort == 'price_asc': order = 'list_price asc'
        elif sort == 'price_desc': order = 'list_price desc'
        elif sort == 'name_asc': order = 'name asc'
        elif sort == 'newest': order = 'create_date desc'

        # 5. Pagination
        items_per_page = 10
        ProductTemplate = request.env['product.template'].sudo() # SUDO for security
        total_products = ProductTemplate.search_count(domain)
        offset = (page - 1) * items_per_page
        total_pages = math.ceil(total_products / items_per_page)
        
        products = ProductTemplate.search(domain, limit=items_per_page, offset=offset, order=order)

        # 6. Fetch Filter Data (Categories & Vendors)
        # We fetch ALL active categories/vendors so the user can filter the search results
        all_categories = request.env['product.public.category'].sudo().search([])
        all_vendors = request.env['marketplace.vendor'].sudo().search([('state', '=', 'active')])

        # 7. URL Query Builder (Keep filters when changing pages)
        filter_params = []
        if search: filter_params.append('search=%s' % search)
        if min_price: filter_params.append('min_price=%s' % min_price)
        if max_price: filter_params.append('max_price=%s' % max_price)
        if vendor: filter_params.append('vendor=%s' % vendor)
        if category: filter_params.append('category=%s' % category)
        if sort: filter_params.append('sort=%s' % sort)
        keep_query = '&'.join(filter_params)

        return request.render("marketplace_platform.search_results_page", {
            'search_term': search,
            'products': products,
            'categories': all_categories,
            'vendors': all_vendors,
            'pager': {
                'current_page': page,
                'total_pages': total_pages,
                'pages': range(1, total_pages + 1),
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_num': page + 1,
                'prev_num': page - 1,
                'keep_query': keep_query
            },
            'filters': {
                'search': search,
                'min_price': min_price,
                'max_price': max_price,
                'vendor': int(vendor) if vendor else None,
                'category': int(category) if category else None,
                'sort': sort
            }
        })

    # CUSTOM CART PAGE
    @http.route('/cart', type='http', auth="public", website=True)
    def aura_cart_view(self, **kw):
        # Get the current order (cart)
        order = request.website.sale_get_order()
        
        # Check if cart exists or is empty
        if not order or order.state != 'draft':
            # Create a simplified object to prevent errors in view if order is None
            order = request.env['sale.order']

        return request.render("marketplace_platform.cart_page", {
            'website_sale_order': order,
        })
        
    # ALL CATEGORIES PAGE
    # ABOUT PAGE
    @http.route(['/about'], type='http', auth="public", website=True)
    def about_page(self, **kw):
        return request.render("marketplace_platform.about_page")
    
    # CONTACT PAGE
    @http.route(['/contactus'], type='http', auth="public", website=True)
    def contact_page(self, **kw):
        return request.render("marketplace_platform.contact_page")
    
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