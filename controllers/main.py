# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import math
import base64

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

    # CUSTOM CART UPDATE (Add to Cart)
    @http.route('/cart/update', type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def cart_update(self, product_id=None, add_qty=1, set_qty=0, **kw):
        """Add product to cart"""
        if not product_id:
            return request.redirect('/cart')
        
        # Get or create sale order
        order = request.website.sale_get_order(force_create=True)
        
        if order.state != 'draft':
            request.website.sale_reset()
            order = request.website.sale_get_order(force_create=True)
        
        # Add product to cart
        product = request.env['product.product'].sudo().browse(int(product_id))
        if product.exists():
            order.sudo()._cart_update(
                product_id=int(product_id),
                add_qty=float(add_qty),
                set_qty=float(set_qty),
            )
        
        return request.redirect('/cart')
    
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
    
    # CUSTOMER ACCOUNT PAGE
    @http.route(['/my/account'], type='http', auth="user", website=True)
    def customer_account(self, section='dashboard', **kw):
        """Customer account dashboard"""
        partner = request.env.user.partner_id
        
        # Get orders
        orders = request.env['sale.order'].search([
            ('partner_id', 'child_of', partner.id)
        ], order='date_order desc')
        
        # Get addresses (delivery addresses)
        addresses = request.env['res.partner'].search([
            '|', ('id', '=', partner.id),
            ('parent_id', '=', partner.id)
        ])
        
        # Get countries for address form
        countries = request.env['res.country'].sudo().search([])
        
        # Calculate stats
        total_orders = len(orders)
        pending_orders = len(orders.filtered(lambda o: o.state in ['draft', 'sent']))
        wishlist_count = 0  # Placeholder for wishlist
        
        values = {
            'section': section,
            'partner': partner,
            'user_id': request.env.user,
            'orders': orders,
            'addresses': addresses,
            'countries': countries,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'wishlist_count': wishlist_count,
        }
        
        return request.render("marketplace_platform.customer_account_page", values)
    
    # UPDATE PROFILE
    @http.route(['/my/account/update'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def customer_account_update(self, section='profile', **post):
        """Update customer profile"""
        partner = request.env.user.partner_id
        user = request.env.user
        
        try:
            # Update basic info
            if post.get('name'):
                partner.sudo().write({'name': post.get('name')})
                user.sudo().write({'name': post.get('name')})
            
            if post.get('email'):
                partner.sudo().write({'email': post.get('email')})
                user.sudo().write({'login': post.get('email')})
            
            if post.get('phone'):
                partner.sudo().write({'phone': post.get('phone')})
            
            if post.get('mobile'):
                partner.sudo().write({'mobile': post.get('mobile')})
            
            # Handle password change
            if post.get('old_password') and post.get('new_password'):
                if post.get('new_password') == post.get('confirm_password'):
                    user.sudo().write({'password': post.get('new_password')})
        
        except Exception as e:
            pass
        
        return request.redirect('/my/account?section=' + section)
    
    # ADD ADDRESS
    @http.route(['/my/account/address/add'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def add_address(self, **post):
        """Add new shipping address"""
        partner = request.env.user.partner_id
        
        try:
            country = request.env['res.country'].sudo().browse(int(post.get('country_id', 0)))
            
            request.env['res.partner'].sudo().create({
                'name': post.get('name'),
                'parent_id': partner.id,
                'type': 'delivery',
                'street': post.get('street'),
                'street2': post.get('street2'),
                'city': post.get('city'),
                'zip': post.get('zip'),
                'country_id': country.id if country else False,
                'phone': post.get('phone'),
            })
        except Exception as e:
            pass
        
        return request.redirect('/my/account?section=addresses')
    
    # DELETE ADDRESS
    @http.route(['/my/account/address/delete/<int:address_id>'], type='http', auth="user", website=True)
    def delete_address(self, address_id, **kw):
        """Delete shipping address"""
        partner = request.env.user.partner_id
        
        address = request.env['res.partner'].sudo().browse(address_id)
        if address.exists() and address.parent_id.id == partner.id:
            address.unlink()
        
        return request.redirect('/my/account?section=addresses')
    
    # SHOW REGISTRATION FORM
    @http.route('/marketplace/register', type='http', auth="user", website=True)
    def vendor_registration(self, **kw):
        partner = request.env.user.partner_id
        
        # Check if already a vendor or has pending request
        existing_vendor = request.env['marketplace.vendor'].sudo().search([
            ('partner_id', '=', partner.id)
        ], limit=1)
        
        if existing_vendor:
            if existing_vendor.state == 'active':
                return request.redirect('/my/marketplace') # Go to dashboard
            elif existing_vendor.state == 'new':
                return request.render("marketplace_platform.vendor_registration_success", {
                    'pending': True,
                    'user_id': request.env.user
                })
        
        return request.render("marketplace_platform.vendor_registration_form", {
            'error': kw.get('error'),
            'values': kw,
            'user_id': request.env.user
        })

    # HANDLE FORM SUBMISSION
    @http.route('/marketplace/register/submit', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def vendor_registration_submit(self, **post):
        partner = request.env.user.partner_id
        
        # Simple Validation
        if not post.get('shop_name') or not post.get('shop_url'):
            return request.redirect('/marketplace/register?error=Name and URL are required')

        try:
            # Create the Vendor Request (Status: New)
            request.env['marketplace.vendor'].sudo().create({
                'partner_id': partner.id,
                'shop_name': post.get('shop_name'),
                'shop_url': post.get('shop_url').lower().replace(' ', '-'),
                'phone': post.get('phone'),
                'email': post.get('email'),
                'description': post.get('description'),
                'state': 'new', # Admin must approve
            })
            return request.render("marketplace_platform.vendor_registration_success", {
                'pending': True,
                'user_id': request.env.user
            })
            
        except Exception as e:
            return request.redirect('/marketplace/register?error=Shop URL already exists or invalid data.')
        
    # VENDOR PRODUCT LIST
    @http.route(['/my/marketplace/products', '/my/marketplace/products/page/<int:page>'], type='http', auth="user", website=True)
    def vendor_products_list(self, page=1, search='', sortby='newest', **kw):
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor:
            return request.redirect('/marketplace/register')

        # Base Domain
        domain = [('vendor_id', '=', vendor.id)]

        # Search Logic
        if search:
            domain += ['|', ('name', 'ilike', search), ('default_code', 'ilike', search)]

        # Sorting
        sort_mappings = {
            'name': 'name asc',
            'price': 'list_price desc',
            'newest': 'create_date desc'
        }
        order = sort_mappings.get(sortby, 'create_date desc')

        # Pagination
        Product = request.env['product.template'].sudo()
        items_per_page = 20
        total_products = Product.search_count(domain)
        
        pager = request.website.pager(
            url='/my/marketplace/products',
            total=total_products,
            page=page,
            step=items_per_page,
            url_args={'search': search, 'sortby': sortby}
        )
        
        offset = (page - 1) * items_per_page
        products = Product.search(domain, limit=items_per_page, offset=offset, order=order)

        values = {
            'page_name': 'products',
            'vendor': vendor,
            'products': products,
            'pager': pager,
            'search': search,
            'sortby': sortby,
            'user_id': request.env.user,
        }
        return request.render("marketplace_platform.vendor_product_list", values)
    
    # UPDATE PRODUCT QUANTITY
    @http.route('/my/marketplace/product/update_quantity/<int:product_id>', type='json', auth="user", website=True)
    def vendor_product_update_quantity(self, product_id, quantity, **kw):
        """JSON endpoint to update product quantity"""
        try:
            product = request.env['product.template'].sudo().browse(product_id)
            current_vendor = request.env['marketplace.vendor'].search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
            
            if not product.exists() or product.vendor_id != current_vendor:
                return {'success': False, 'error': 'Product not found or access denied'}
            
            # Update quantity
            warehouse = request.website.warehouse_id
            if not warehouse:
                warehouse = request.env['stock.warehouse'].sudo().search([('company_id', '=', request.website.company_id.id)], limit=1)
            
            if warehouse and warehouse.lot_stock_id:
                quant = request.env['stock.quant'].sudo().search([
                    ('product_id', '=', product.product_variant_id.id),
                    ('location_id', '=', warehouse.lot_stock_id.id)
                ], limit=1)
                
                if quant:
                    quant.sudo().write({'quantity': float(quantity)})
                else:
                    request.env['stock.quant'].sudo().create({
                        'product_id': product.product_variant_id.id,
                        'location_id': warehouse.lot_stock_id.id,
                        'quantity': float(quantity),
                    })
                
                return {'success': True, 'new_quantity': float(quantity)}
            
            return {'success': False, 'error': 'Warehouse not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # DELETE PRODUCT ACTION
    @http.route('/my/marketplace/product/delete/<int:product_id>', type='http', auth="user", website=True)
    def vendor_product_delete(self, product_id, **kw):
        # Security Check: Ensure product belongs to current vendor
        product = request.env['product.template'].sudo().browse(product_id)
        current_vendor = request.env['marketplace.vendor'].search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        
        if product.exists() and product.vendor_id == current_vendor:
            product.unlink() # Or set to archived: product.active = False
        
        return request.redirect('/my/marketplace/products')
    
    # DUPLICATE PRODUCT ACTION
    @http.route('/my/marketplace/product/duplicate/<int:product_id>', type='http', auth="user", website=True)
    def vendor_product_duplicate(self, product_id, **kw):
        product = request.env['product.template'].sudo().browse(product_id)
        current_vendor = request.env['marketplace.vendor'].search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        
        if product.exists() and product.vendor_id == current_vendor:
            new_product = product.copy({
                'name': product.name + ' (Copy)',
                'is_published': False, # Start as draft
                'approval_state': 'draft'
            })
            
        return request.redirect('/my/marketplace/products')
    
    # RENDER ADD PRODUCT PAGE
    @http.route('/my/marketplace/products/add', type='http', auth="user", website=True)
    def vendor_product_add(self, **kw):
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor or vendor.state != 'active':
            return request.redirect('/marketplace/register')
            
        categories = request.env['product.public.category'].sudo().search([])
        
        return request.render("marketplace_platform.vendor_add_product_page", {
            'page_name': 'products',
            'vendor': vendor,
            'categories': categories,
            'error': kw.get('error'),
            'user_id': request.env.user,
        })

    # HANDLE FORM SUBMISSION
    @http.route('/my/marketplace/products/submit', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def vendor_product_submit(self, **post):
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor:
            return request.redirect('/marketplace/register')

        try:
            # 1. Handle Image
            image_data = False
            if 'image' in request.params:
                file = request.params['image']
                if hasattr(file, 'read') and hasattr(file, 'filename') and file.filename:
                    image_data = base64.b64encode(file.read())

            # 2. Prepare Data
            vals = {
                'name': post.get('name'),
                'description_sale': post.get('description'),
                'list_price': float(post.get('price') or 0.0),
                'detailed_type': 'product',
                'vendor_id': vendor.id,
                'approval_state': 'pending', 
                'is_published': post.get('is_published') == 'on',
                'website_id': request.website.id,
            }

            if image_data:
                vals['image_1920'] = image_data

            if post.get('category_id'):
                vals['public_categ_ids'] = [(4, int(post.get('category_id')))]

            if post.get('compare_price'):
                vals['compare_list_price'] = float(post.get('compare_price'))

            if post.get('weight'): 
                vals['weight'] = float(post.get('weight'))
            
            # 3. Create Product
            product_tmpl = request.env['product.template'].sudo().create(vals)

            # 4. Handle Stock - Direct quantity update without inventory adjustment validation
            qty = float(post.get('quantity') or 0.0)
            if qty > 0:
                warehouse = request.website.warehouse_id
                if not warehouse:
                    warehouse = request.env['stock.warehouse'].sudo().search([('company_id', '=', request.website.company_id.id)], limit=1)
                
                if warehouse and warehouse.lot_stock_id:
                    # Check if quant already exists
                    quant = request.env['stock.quant'].sudo().search([
                        ('product_id', '=', product_tmpl.product_variant_id.id),
                        ('location_id', '=', warehouse.lot_stock_id.id)
                    ], limit=1)
                    
                    if quant:
                        # Update existing quant directly
                        quant.sudo().write({'quantity': qty})
                    else:
                        # Create new quant with direct quantity (bypasses inventory adjustment)
                        request.env['stock.quant'].sudo().create({
                            'product_id': product_tmpl.product_variant_id.id,
                            'location_id': warehouse.lot_stock_id.id,
                            'quantity': qty,  # Use 'quantity' not 'inventory_quantity'
                        })

            return request.redirect('/my/marketplace/products?success=pending')

        except Exception as e:
            return request.redirect('/my/marketplace/products/add?error=' + str(e))
                
    # RENDER EDIT PRODUCT PAGE
    @http.route('/my/marketplace/product/edit/<int:product_id>', type='http', auth="user", website=True)
    def vendor_product_edit(self, product_id, **kw):
        partner = request.env.user.partner_id
        
        # Security: Check if vendor exists
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        if not vendor:
            return request.redirect('/marketplace/register')
            
        # Security: Check if product belongs to this vendor
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists() or product.vendor_id.id != vendor.id:
            return request.redirect('/my/marketplace/products') # Redirect if trying to access others' products
            
        # Fetch Categories for dropdown
        categories = request.env['product.public.category'].sudo().search([])
        
        return request.render("marketplace_platform.vendor_edit_product_page", {
            'page_name': 'products',
            'vendor': vendor,
            'product': product,
            'categories': categories,
            'error': kw.get('error')
        })

    # 2. HANDLE EDIT SUBMISSION
    @http.route('/my/marketplace/product/edit/submit/<int:product_id>', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def vendor_product_edit_submit(self, product_id, **post):
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists() or product.vendor_id.id != vendor.id:
            return request.redirect('/my/marketplace/products')

        try:
            # 1. Update Data
            vals = {
                'name': post.get('name'),
                'description_sale': post.get('description'),
                'list_price': float(post.get('price') or 0.0),
                'compare_list_price': float(post.get('compare_price') or 0.0),
                'is_published': post.get('is_published') == 'on',
            }

            if post.get('weight'):
                vals['weight'] = float(post.get('weight'))

            if post.get('category_id'):
                vals['public_categ_ids'] = [(6, 0, [int(post.get('category_id'))])]

            if 'image' in request.params:
                file = request.params['image']
                if hasattr(file, 'read') and hasattr(file, 'filename') and file.filename:
                    vals['image_1920'] = base64.b64encode(file.read())

            product.write(vals)

            # 2. Update Stock - Direct quantity update without inventory adjustment validation
            if 'quantity' in post:
                new_qty = float(post.get('quantity') or 0.0)
                
                warehouse = request.website.warehouse_id
                if not warehouse:
                    warehouse = request.env['stock.warehouse'].sudo().search([('company_id', '=', request.website.company_id.id)], limit=1)
                
                if warehouse and warehouse.lot_stock_id:
                    # Find existing quant for this product
                    quant = request.env['stock.quant'].sudo().search([
                        ('product_id', '=', product.product_variant_id.id),
                        ('location_id', '=', warehouse.lot_stock_id.id)
                    ], limit=1)
                    
                    if quant:
                        # Update existing quant directly
                        quant.sudo().write({'quantity': new_qty})
                    else:
                        # Create new quant with direct quantity
                        request.env['stock.quant'].sudo().create({
                            'product_id': product.product_variant_id.id,
                            'location_id': warehouse.lot_stock_id.id,
                            'quantity': new_qty,
                        })

            return request.redirect('/my/marketplace/products')

        except Exception as e:
            return request.redirect('/my/marketplace/product/edit/%s?error=%s' % (product_id, str(e)))        
        
    # VENDOR ORDERS LIST
# ... inside MarketplaceController ...

    # VENDOR ORDERS LIST
    @http.route(['/my/marketplace/orders', '/my/marketplace/orders/page/<int:page>'], type='http', auth="user", website=True)
    def vendor_orders_list(self, page=1, search='', status='all', **kw):
        # 1. Get Vendor
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor:
            return request.redirect('/marketplace/register')

        # 2. Search for Order Lines (Sudo to see all lines)
        SaleLine = request.env['sale.order.line'].sudo()
        
        # Base domain: Lines containing this vendor's products
        line_domain = [('product_id.product_tmpl_id.vendor_id', '=', vendor.id)]
        
        # Search Filter
        if search:
            line_domain += ['|', ('order_id.name', 'ilike', search), ('order_id.partner_id.name', 'ilike', search)]
            
        # Status Filter
        if status != 'all':
            line_domain += [('order_id.state', '=', status)]

        # Fetch lines
        vendor_lines = SaleLine.search(line_domain)
        
        # 3. Group by Order
        # We use mapped to get unique orders, then sort by date (newest first)
        order_ids = vendor_lines.mapped('order_id')
        
        # Manual sorting because mapped() returns unsorted recordset
        # We handle the case where date_order might be missing (rare but safer)
        order_ids = order_ids.sorted(key=lambda r: r.date_order or r.create_date, reverse=True)

        # 4. Pagination (Python Slicing)
        items_per_page = 15
        total_orders = len(order_ids)
        
        pager = request.website.pager(
            url='/my/marketplace/orders',
            total=total_orders,
            page=page,
            step=items_per_page,
            url_args={'search': search, 'status': status}
        )
        
        # Slice the recordset for the current page
        start = (page - 1) * items_per_page
        end = start + items_per_page
        orders_page = order_ids[start:end]

        # 5. Calculate Vendor-Specific Totals
        orders_data = []
        for order in orders_page:
            # Filter lines AGAIN to calculate only THIS vendor's share
            # (An order might have $100 total, but only $20 is for this vendor)
            my_lines = order.order_line.filtered(lambda l: l.product_id.product_tmpl_id.vendor_id.id == vendor.id)
            
            vendor_total = sum(my_lines.mapped('price_subtotal'))
            product_names = ", ".join(my_lines.mapped('product_id.name'))
            total_qty = sum(my_lines.mapped('product_uom_qty'))
            
            orders_data.append({
                'order': order,
                'vendor_total': vendor_total,
                'products_display': product_names,
                'item_count': int(total_qty)
            })

        values = {
            'page_name': 'orders',
            'vendor': vendor,
            'orders_data': orders_data,
            'pager': pager,
            'search': search,
            'status': status,
            'user_id': request.env.user,
        }
        return request.render("marketplace_platform.vendor_order_list", values)
        
    @http.route(['/my/marketplace'], type='http', auth="user", website=True)
    def vendor_dashboard(self, **kw):
        user = request.env.user
        partner = user.partner_id
        
        # 1. Get Vendor Profile
        # Assuming you linked partner -> vendor in previous steps
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor or vendor.state != 'active':
            return request.redirect('/marketplace/register')

        # 2. Calculate Metrics
        
        # Products
        active_products_count = request.env['product.template'].search_count([
            ('vendor_id', '=', vendor.id),
            ('is_published', '=', True)
        ])
        
        # Sales (Lines belonging to this vendor)
        # We search Order Lines where the product belongs to the vendor
        vendor_lines = request.env['sale.order.line'].search([
            ('state', 'in', ['sale', 'done']),
            ('product_id.product_tmpl_id.vendor_id', '=', vendor.id)
        ])
        
        total_sales_amount = sum(vendor_lines.mapped('price_subtotal'))
        total_orders_count = len(vendor_lines.mapped('order_id'))
        
        # Recent Orders (Get the last 5 distinct orders)
        recent_orders = vendor_lines.mapped('order_id').sorted(key=lambda r: r.date_order, reverse=True)[:5]

        values = {
            'page_name': 'dashboard', # For navbar active state
            'vendor': vendor,
            'metrics': {
                'sales': total_sales_amount,
                'orders': total_orders_count,
                'products': active_products_count,
                'balance': vendor.balance, # From your model
            },
            'recent_orders': recent_orders,
            'user_id': request.env.user,
        }
        
        return request.render("marketplace_platform.portal_vendor_dashboard", values)