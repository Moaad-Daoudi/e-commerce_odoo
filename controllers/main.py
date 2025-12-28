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
        
        # fetch categories (only featured ones)
        categories = request.env['product.public.category'].sudo().search([('is_featured', '=', True)], limit=6)

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
    def cart_update(self, product_id=None, line_id=None, add_qty=None, remove_qty=None, set_qty=None, **kw):
        """Add product to cart or update cart line quantities"""
        order = request.website.sale_get_order()
        
        # Handle line_id based update (from cart page)
        if line_id:
            if not order or order.state != 'draft':
                return request.redirect('/cart')
                
            line = request.env['sale.order.line'].sudo().browse(int(line_id))
            if line.exists() and line.order_id == order:
                # Calculate new quantity
                if set_qty is not None:
                    new_qty = float(set_qty)
                elif add_qty:
                    new_qty = line.product_uom_qty + float(add_qty)
                elif remove_qty:
                    new_qty = line.product_uom_qty - float(remove_qty)
                else:
                    new_qty = line.product_uom_qty
                
                # Update or remove line
                if new_qty <= 0:
                    line.unlink()
                else:
                    line.sudo().write({'product_uom_qty': new_qty})
            
            return request.redirect('/cart')
        
        # Handle product_id based update (add to cart from product page)
        if not product_id:
            return request.redirect('/cart')
        
        # Get or create sale order
        if not order:
            order = request.website.sale_get_order(force_create=True)
        
        if order.state != 'draft':
            request.website.sale_reset()
            order = request.website.sale_get_order(force_create=True)
        
        # Add product to cart
        product = request.env['product.product'].sudo().browse(int(product_id))
        if product.exists():
            qty = float(add_qty) if add_qty else 1.0
            order.sudo()._cart_update(
                product_id=int(product_id),
                add_qty=qty,
                set_qty=float(set_qty) if set_qty is not None else 0,
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
        wishlist_count = request.env['product.wishlist'].search_count([('partner_id', '=', partner.id)])
        
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
            # Handle profile image upload
            if 'image' in request.params:
                file = request.params['image']
                if hasattr(file, 'read') and hasattr(file, 'filename') and file.filename:
                    image_data = base64.b64encode(file.read())
                    partner.sudo().write({'image_1920': image_data})
            
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
    
    # VIEW ORDER DETAILS
    @http.route(['/my/orders/<int:order_id>'], type='http', auth="user", website=True)
    def order_detail(self, order_id, **kw):
        """View detailed order information"""
        partner = request.env.user.partner_id
        
        # Get the order and verify it belongs to the user
        order = request.env['sale.order'].sudo().search([
            ('id', '=', order_id),
            ('partner_id', 'child_of', partner.id)
        ], limit=1)
        
        if not order:
            return request.redirect('/my/account?section=orders')
        
        # Calculate delivery status based on order state and picking state
        delivery_status = 'pending'
        if order.state == 'done':
            delivery_status = 'delivered'
        elif order.state == 'sale':
            # Check if there are pickings (deliveries)
            pickings = request.env['stock.picking'].sudo().search([
                ('sale_id', '=', order.id)
            ])
            if pickings:
                if any(p.state == 'done' for p in pickings):
                    delivery_status = 'delivered'
                elif any(p.state in ['confirmed', 'assigned'] for p in pickings):
                    delivery_status = 'shipped'
            else:
                delivery_status = 'processing'
        
        # Calculate estimated delivery date
        estimated_delivery = False
        if order.state in ['sale', 'done'] and delivery_status != 'delivered':
            # Estimate 3-7 business days from order confirmation
            from datetime import datetime, timedelta
            order_date = order.date_order
            estimated_days = 7  # default to 7 days
            estimated_date = order_date + timedelta(days=estimated_days)
            estimated_delivery = estimated_date.strftime('%B %d, %Y')
        
        values = {
            'order': order,
            'delivery_status': delivery_status,
            'estimated_delivery': estimated_delivery,
        }
        
        return request.render("marketplace_platform.customer_order_detail_page", values)
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
    
    # VIEW ORDER DETAILS
    @http.route('/my/marketplace/order/<int:order_id>', type='http', auth="user", website=True)
    def vendor_order_detail(self, order_id, **kw):
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor:
            return request.redirect('/marketplace/register')

        # Sudo to read order details
        order = request.env['sale.order'].sudo().browse(order_id)
        
        # Security: Ensure this order actually contains products from this vendor
        vendor_lines = order.order_line.filtered(lambda l: l.product_id.product_tmpl_id.vendor_id.id == vendor.id)
        
        if not vendor_lines:
            return request.redirect('/my/marketplace/orders')

        # Calculate Vendor specific totals
        vendor_total = sum(vendor_lines.mapped('price_subtotal'))
        
        # Find related delivery (Picking) for status update
        # Assuming stock logic splits pickings by vendor (standard Odoo behavior if routes are set)
        # OR we just look for any picking containing these products
        picking = request.env['stock.picking'].sudo().search([
            ('origin', '=', order.name),
            ('move_ids.product_id', 'in', vendor_lines.mapped('product_id').ids),
            ('state', 'not in', ['cancel', 'done'])
        ], limit=1)

        return request.render("marketplace_platform.vendor_order_detail", {
            'page_name': 'orders',
            'vendor': vendor,
            'order': order,
            'vendor_lines': vendor_lines,
            'vendor_total': vendor_total,
            'picking': picking, # To show "Ship" button
        })

    # ACTION: MARK AS SHIPPED
    @http.route('/my/marketplace/order/ship/<int:picking_id>', type='http', auth="user", website=True)
    def vendor_order_ship(self, picking_id, **kw):
        # Allow vendor to validate the delivery
        picking = request.env['stock.picking'].sudo().browse(picking_id)
        
        if picking.exists() and picking.state not in ['done', 'cancel']:
            # Simple validation: Mark all qty as done and validate
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
            picking.button_validate()
            
        return request.redirect(request.httprequest.referrer or '/my/marketplace/orders')
    
    # ... inside MarketplaceController ...

    # 1. RENDER SETTINGS PAGE
    @http.route('/my/marketplace/settings', type='http', auth="user", website=True)
    def vendor_settings(self, **kw):
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor:
            return request.redirect('/marketplace/register')
            
        countries = request.env['res.country'].sudo().search([])

        return request.render("marketplace_platform.vendor_settings_page", {
            'page_name': 'profile', # Highlights 'Profile' in navbar
            'vendor': vendor,
            'countries': countries,
            'success': kw.get('success')
        })

    # 2. HANDLE SETTINGS SAVE
    @http.route('/my/marketplace/settings/submit', type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def vendor_settings_submit(self, **post):
        partner = request.env.user.partner_id
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor:
            return request.redirect('/marketplace/register')

        vals = {
            'shop_name': post.get('shop_name'),
            'description': post.get('description'),
            'phone': post.get('phone'),
            'email': post.get('email'),
            # Socials
            'social_facebook': post.get('social_facebook'),
            'social_instagram': post.get('social_instagram'),
            'social_twitter': post.get('social_twitter'),
            # Address (Writing to related partner fields)
            'street': post.get('street'),
            'city': post.get('city'),
            'zip': post.get('zip'),
        }
        
        if post.get('country_id'):
            vals['country_id'] = int(post.get('country_id'))

        # Handle Images
        if 'image_banner' in request.params:
            file = request.params['image_banner']
            if hasattr(file, 'read') and file.filename:
                vals['image_1920'] = base64.b64encode(file.read())

        if 'image_logo' in request.params:
            file = request.params['image_logo']
            if hasattr(file, 'read') and file.filename:
                vals['image_128'] = base64.b64encode(file.read())

        # Write changes
        vendor.sudo().write(vals)
        
        return request.redirect('/my/marketplace/settings?success=1')
    
    # ... inside MarketplaceController ...

    # 1. WISHLIST PAGE
    @http.route(['/wishlist'], type='http', auth="public", website=True)
    def aura_wishlist_view(self, sort='date_desc', **kw):
        # Guests store wishlist in session or cookies usually, but Odoo's model requires a partner.
        # For simplicity in this custom build, we enforce login or use the public user (not recommended for persistent wishlist).
        # Assuming User is logged in for full features:
        if request.env.user._is_public():
            return request.redirect('/login?redirect=/wishlist')

        try:
            Wishlist = request.env['product.wishlist'].sudo()
            domain = [('partner_id', '=', request.env.user.partner_id.id)]
            
            # Sorting Logic
            order = 'create_date desc'
            if sort == 'date_asc': order = 'create_date asc'
            elif sort == 'price_desc': order = 'price desc' # price is a related field in wishlist
            elif sort == 'price_asc': order = 'price asc'
            
            wishlist_items = Wishlist.search(domain, order=order)

            return request.render("marketplace_platform.wishlist_page", {
                'wishlist_items': wishlist_items,
                'sort': sort,
            })
        except Exception as e:
            import logging
            import traceback
            _logger = logging.getLogger(__name__)
            _logger.error("Error loading wishlist: %s", str(e))
            _logger.error("Traceback: %s", traceback.format_exc())
            # Return empty wishlist on error
            return request.render("marketplace_platform.wishlist_page", {
                'wishlist_items': request.env['product.wishlist'].sudo(),
                'sort': sort,
            })


    # ADD TO WISHLIST
    @http.route('/wishlist/add/<int:product_tmpl_id>', type='http', auth="user", website=True)
    def aura_wishlist_add(self, product_tmpl_id, **kw):
        partner = request.env.user.partner_id
        product_tmpl = request.env['product.template'].browse(product_tmpl_id)
        
        if product_tmpl.exists() and product_tmpl.product_variant_ids:
            product_variant = product_tmpl.product_variant_ids[0]
            Wishlist = request.env['product.wishlist']
            
            # Check if already in wishlist
            existing = Wishlist.search([
                ('partner_id', '=', partner.id),
                ('product_id', '=', product_variant.id)
            ], limit=1)
            
            if not existing:
                # Add to wishlist
                Wishlist._add_to_wishlist(
                    partner_id=partner.id,
                    product_id=product_variant.id,
                    website_id=request.website.id if hasattr(request, 'website') else None
                )
        
        return request.redirect(request.httprequest.referrer or '/')
    
    # REMOVE FROM WISHLIST (by product template id)
    @http.route('/wishlist/remove/<int:product_tmpl_id>', type='http', auth="user", website=True)
    def aura_wishlist_remove(self, product_tmpl_id, **kw):
        partner = request.env.user.partner_id
        product_tmpl = request.env['product.template'].browse(product_tmpl_id)
        
        if product_tmpl.exists() and product_tmpl.product_variant_ids:
            product_variant = product_tmpl.product_variant_ids[0]
            Wishlist = request.env['product.wishlist']
            
            # Find and remove from wishlist
            wishlist_item = Wishlist.search([
                ('partner_id', '=', partner.id),
                ('product_id', '=', product_variant.id)
            ], limit=1)
            
            if wishlist_item:
                wishlist_item.unlink()
        
        return request.redirect(request.httprequest.referrer or '/')
    
    # 3. ACTION: REMOVE SINGLE ITEM
    @http.route(['/wishlist/remove/<int:wishlist_id>'], type='http', auth="user", website=True)
    def wishlist_remove(self, wishlist_id, **kw):
        wish_item = request.env['product.wishlist'].browse(wishlist_id)
        if wish_item.exists() and wish_item.partner_id == request.env.user.partner_id:
            wish_item.unlink()
        return request.redirect('/wishlist')

    # 4. BULK: MOVE ALL TO CART
    @http.route(['/wishlist/move_all'], type='http', auth="user", website=True)
    def wishlist_move_all(self, **kw):
        partner = request.env.user.partner_id
        wishlist_items = request.env['product.wishlist'].search([('partner_id', '=', partner.id)])
        
        if wishlist_items:
            order = request.website.sale_get_order(force_create=True)
            for item in wishlist_items:
                # Add to cart
                order._cart_update(product_id=item.product_id.id, add_qty=1)
                # Delete from wishlist
                item.unlink()
                
        return request.redirect('/cart')

    # 5. BULK: CLEAR ALL
    @http.route(['/wishlist/clear'], type='http', auth="user", website=True)
    def wishlist_clear(self, **kw):
        partner = request.env.user.partner_id
        wishlist_items = request.env['product.wishlist'].search([('partner_id', '=', partner.id)])
        wishlist_items.unlink()
        return request.redirect('/wishlist')
        
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
        vendor_lines = request.env['sale.order.line'].sudo().search([
            ('order_id.state', 'in', ['sale', 'done']),
            ('product_id.product_tmpl_id.vendor_id', '=', vendor.id)
        ])
        
        total_sales_amount = sum(vendor_lines.mapped('price_subtotal'))
        total_orders_count = len(set(vendor_lines.mapped('order_id.id')))
        
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
    
    # VENDOR INCOME & COMMISSION PAGE
    @http.route(['/my/marketplace/income'], type='http', auth="user", website=True)
    def vendor_income(self, **kw):
        user = request.env.user
        partner = user.partner_id
        
        # Get Vendor Profile
        vendor = request.env['marketplace.vendor'].search([('partner_id', '=', partner.id)], limit=1)
        
        if not vendor or vendor.state != 'active':
            return request.redirect('/marketplace/register')

        # Get all commissions for this vendor
        commissions = request.env['marketplace.commission'].sudo().search([
            ('vendor_id', '=', vendor.id)
        ], order='create_date desc')
        
        # Calculate totals
        confirmed_commissions = commissions.filtered(lambda c: c.state in ['confirmed', 'paid'])
        paid_commissions = commissions.filtered(lambda c: c.state == 'paid')
        
        total_earnings = sum(confirmed_commissions.mapped('sale_amount')) if confirmed_commissions else 0.0
        total_commission = sum(confirmed_commissions.mapped('amount_commission')) if confirmed_commissions else 0.0
        net_income = total_earnings - total_commission
        available_balance = sum(confirmed_commissions.mapped('vendor_amount')) - sum(paid_commissions.mapped('vendor_amount')) if confirmed_commissions else 0.0

        values = {
            'page_name': 'income',
            'vendor': vendor,
            'commissions': commissions,
            'total_earnings': total_earnings,
            'total_commission': total_commission,
            'net_income': net_income,
            'available_balance': available_balance,
            'user_id': request.env.user,
        }
        
        return request.render("marketplace_platform.vendor_income_page", values)
    
    # CUSTOM CHECKOUT ROUTES
    @http.route(['/shop/checkout/address'], type='http', auth="public", website=True)
    def custom_checkout_address(self, **kw):
        """Custom shipping address page"""
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            return request.redirect('/cart')
        
        countries = request.env['res.country'].sudo().search([])
        
        return request.render("marketplace_platform.custom_address_page", {
            'website_sale_order': order.sudo(),
            'countries': countries,
        })
    
    @http.route(['/shop/checkout/payment'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def custom_checkout_payment(self, **post):
        """Save address and show payment page"""
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            return request.redirect('/cart')
        
        # Save address data to order if POST request
        if request.httprequest.method == 'POST' and post.get('name'):
            try:
                partner_values = {
                    'name': post.get('name', ''),
                    'email': post.get('email', ''),
                    'phone': post.get('phone', ''),
                    'street': post.get('street', ''),
                    'city': post.get('city', ''),
                    'zip': post.get('zip', ''),
                }
                
                if post.get('country_id'):
                    partner_values['country_id'] = int(post.get('country_id'))
                
                order.partner_id.sudo().write(partner_values)
            except Exception as e:
                pass
        
        return request.render("marketplace_platform.custom_payment_page", {
            'website_sale_order': order.sudo(),
        })
    
    @http.route(['/shop/checkout/confirm'], type='http', auth="public", website=True, csrf=False)
    def custom_checkout_confirm(self, **kw):
        """Confirm order and process payment"""
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            return request.redirect('/cart')
        
        try:
            # Save the order name before clearing cart
            order_name = order.name
            
            # Instead of action_confirm, just change state to 'sale'
            # This avoids all the vendor access issues
            order.sudo().write({'state': 'sale'})
            
            # Clear the cart session
            request.website.sale_reset()
            
            # Show success page
            return request.render("marketplace_platform.order_confirmation_page", {
                'order_name': order_name,
            })
        except Exception as e:
            # Log the error for debugging
            import logging
            import traceback
            _logger = logging.getLogger(__name__)
            _logger.error("Error confirming order: %s", str(e))
            _logger.error("Traceback: %s", traceback.format_exc())
            
            # If error, redirect back to cart
            return request.redirect('/cart?error=checkout_failed')
        
    # OUR STORY (About Us)
    @http.route('/about-us', type='http', auth="public", website=True)
    def about_us_page(self, **kw):
        return request.render("marketplace_platform.about_us_page")

    # ==========================================================================
    # 5. CAREERS & JOBS (Connecté au Backend hr.job)
    # ==========================================================================

    @http.route('/jobs', type='http', auth="public", website=True)
    def jobs(self, **kw):
        # 1. Récupération des postes ouverts et publiés depuis la DB
        Job = request.env['hr.job'].sudo()
        
        # CORRECTION : On retire ('state', '=', 'recruit')
        # On garde uniquement le filtre sur la publication web
        job_records = Job.search([
            ('website_published', '=', True) 
        ])
        
        # 2. Transformation pour le template
        jobs_data = []
        for job in job_records:
            # Sécurité : Si département ou adresse manquent, on met une valeur par défaut
            dept_name = job.department_id.name if job.department_id else 'General'
            loc_name = job.address_id.city if job.address_id else 'Remote'
            
            jobs_data.append({
                'id': job.id,
                'title': job.name,
                'type': 'Full-time', 
                'location': loc_name,
                'dept': dept_name,
            })

        return request.render("marketplace_platform.careers_page", {'jobs': jobs_data})

    @http.route(['/jobs/apply/<int:job_id>', '/jobs/apply/general'], type='http', auth="public", website=True)
    def jobs_apply(self, job_id=None, **kw):
        job_title = "General Application"
        
        # Récupération dynamique du titre
        if job_id:
            job = request.env['hr.job'].sudo().browse(job_id)
            if job.exists():
                job_title = job.name
        
        return request.render("marketplace_platform.job_application_page", {
            'job_title': job_title,
            'job_id': job_id
        })

    @http.route('/jobs/submit', type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def jobs_submit(self, **post):
        # Récupération des données
        job_id = post.get('job_id')
        partner_name = f"{post.get('name')} {post.get('surname')}"
        
        # Création dynamique de la candidature
        vals = {
            'name': f"{partner_name} - {post.get('email')}", # Sujet
            'partner_name': partner_name,
            'email_from': post.get('email'),
            'description': f"LinkedIn: {post.get('linkedin')}\n\nLettre:\n{post.get('cover_letter')}",
        }
        
        # Lier au poste spécifique si existant
        if job_id:
            vals['job_id'] = int(job_id)

        # Création en base
        applicant = request.env['hr.applicant'].sudo().create(vals)

        # Gestion du CV (Pièce jointe)
        resume_file = post.get('resume')
        if resume_file:
            request.env['ir.attachment'].sudo().create({
                'name': resume_file.filename,
                'datas': base64.b64encode(resume_file.read()),
                'res_model': 'hr.applicant',
                'res_id': applicant.id,
                'type': 'binary',
            })

        return request.render("marketplace_platform.job_thank_you_page")

    # BLOG (Custom Page)
    @http.route('/blog', type='http', auth="public", website=True)
    def blog(self, **kw):
        # Récupération des articles publiés via l'ORM Odoo
        BlogPost = request.env['blog.post'].sudo()
        
        # On récupère les articles publiés, triés par date décroissante
        posts = BlogPost.search([
            ('is_published', '=', True)
        ], order='post_date desc', limit=12)
        
        # On identifie le dernier article comme "Featured" pour le design
        featured_post = posts[0] if posts else None
        other_posts = posts[1:] if len(posts) > 1 else []

        return request.render("marketplace_platform.blog_page", {
            'featured_post': featured_post,
            'posts': other_posts
        })

    # ROUTE POUR LIRE UN ARTICLE
    @http.route('/blog/post/<int:post_id>', type='http', auth="public", website=True)
    def blog_post_detail(self, post_id, **kw):
        # Récupération de l'article spécifique
        post = request.env['blog.post'].sudo().browse(post_id)
        
        if not post.exists() or not post.is_published:
            return request.redirect('/blog')
            
        return request.render("marketplace_platform.blog_post_detail_page", {'post': post})
        
    @http.route('/faq', type='http', auth="public", website=True)
    def faq(self, **kw): return request.render("marketplace_platform.faq_page")

    @http.route('/shipping', type='http', auth="public", website=True)
    def shipping(self, **kw): return request.render("marketplace_platform.shipping_page")

    @http.route('/e-terms', type='http', auth="public", website=True)
    def terms(self, **kw): return request.render("marketplace_platform.terms_page")

    @http.route(['/privacy', '/page/website.privacy'], type='http', auth="public", website=True)
    def privacy(self, **kw): return request.render("marketplace_platform.privacy_page")
    

    # GIFT CARDS
    @http.route('/shop/gift-cards', type='http', auth="public", website=True)
    def gift_cards_page(self, **kw):
        # On cherche les produits qui sont des cartes cadeaux (ou on simule)
        # Dans un vrai Odoo, on filtrerait par 'is_gift_card' ou catégorie spécifique
        cards = request.env['product.template'].sudo().search([
            ('is_published', '=', True),
            ('name', 'ilike', 'Card') # Filtre simple pour l'exemple
        ], limit=4)
        return request.render("marketplace_platform.gift_cards_page", {'cards': cards})

    # CHEM YOUR (Collection Page)
    # Interprété comme une page de campagne marketing "Charm Your Home/Life"
    @http.route('/shop/chem-your', type='http', auth="public", website=True)
    def chem_your_page(self, **kw):
        # On récupère quelques produits phares pour cette collection
        featured = request.env['product.template'].sudo().search([
            ('is_published', '=', True)
        ], limit=8, order='list_price desc')
        return request.render("marketplace_platform.chem_your_page", {'products': featured})

    @http.route('/makers', type='http', auth="public", website=True)
    def makers_page(self, page=1, search=None, **kw):
        items_per_page = 12
        Vendor = request.env['marketplace.vendor'].sudo()
        
        # 1. Domaine de base : Vendeurs actifs uniquement
        # ATTENTION : Vérifiez dans votre DB que vos vendeurs sont bien 'active'
        # Si vous testez avec des vendeurs 'new', changez temporairement en :
        # domain = [('state', 'in', ['new', 'active'])]
        domain = [('state', '=', 'active')]
        
        # 2. Logique de Recherche Avancée
        if search:
            # Recherche insensible à la casse sur le Nom OU la Description
            for srch in search.split(" "):
                domain += [
                    '|', 
                    ('shop_name', 'ilike', srch),
                    ('description', 'ilike', srch)
                ]
        
        total_vendors = Vendor.search_count(domain)
        
        # Pagination
        pager = request.website.pager(
            url='/makers',
            total=total_vendors,
            page=page,
            step=items_per_page,
            url_args={'search': search} if search else {}
        )
        
        offset = (page - 1) * items_per_page
        
        # Tri par pertinence (si recherche) ou par ventes (si pas de recherche)
        order = 'sale_count desc'
        
        vendors = Vendor.search(domain, limit=items_per_page, offset=offset, order=order)
        
        return request.render("marketplace_platform.makers_page", {
            'vendors': vendors,
            'pager': pager,
            'search_term': search,
        })
