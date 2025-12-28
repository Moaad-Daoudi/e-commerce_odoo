# -*- coding: utf-8 -*-
{
    'name': "Marketplace Platform",
    'summary': """
        Multi-vendor platform for Odoo:
        Vendor management, commissions, and order separation.
    """,

    'description': """
        Odoo Marketplace - Complete Module
        =================================
        This module transforms Odoo into a B2B/B2C marketplace.

        Main Features:
        - Seller registration and approval
        - Product management per seller
        - Order splitting (one customer order = multiple delivery orders)
        - Automatic commission calculation
        - Payment request management (Payouts)
        - Dedicated seller portal
    """,

    'author': "Ilyas BEL EL YAZID, Moaad Daoudi",
    'category': 'Sales/Marketplace',
    'version': '18.0', 

    'depends': [
        'base',              # Core Odoo functionality
        'web',               # Web interface
        'website',           # Website builder
        'website_sale',      # E-commerce functionality
        'sale',              # Sales management
        'stock',             # Inventory management
        'account',           # Accounting & invoicing
        'portal',            # Customer/vendor portal
        'payment',           # Payment providers
        'contacts',          # Partner/customer management
        'delivery',
        'auth_signup',       # For signup functionality
        'website_hr_recruitment',
        'hr_recruitment',
        'website_blog',
    ],

    'data': [
        'security/groups.xml',
        'security/marketplace_security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/demo_data.xml',
        'data/category_images.xml',
        'data/recruitment_data.xml',
        'views/admin/vendor_views.xml',
        'views/admin/product_views.xml',
        'views/admin/category_views.xml',
        'views/admin/commission_views.xml',
        'views/admin/menu.xml',
        'views/pages/about_us.xml',
        'views/pages/careers.xml',
        'views/pages/blog.xml',
        'views/pages/blog_post.xml',
        'views/pages/blog_views.xml',
        'views/pages/support.xml',
        'views/pages/shop_extras.xml',
        'views/pages/job_application.xml',
        'views/components/navbar.xml',
        'views/components/hero.xml',
        'views/components/featured_section.xml',
        'views/components/footer.xml',
        'views/components/pagination.xml',
        'views/components/vendor_navbar.xml',
        'views/home_page.xml',
        'views/all_categories_page.xml',
        'views/categorie_listing_page.xml',
        'views/product_details_page.xml',
        'views/vendor_profile_page.xml',
        'views/search_results_page.xml',
        'views/cart_page.xml',
        'views/customer_account_page.xml',
        'views/customer_order_detail.xml',
        'views/login_page.xml',
        'views/signup_page.xml',
        'views/about_page.xml',
        'views/contact_page.xml',
        'views/vendor_registration.xml',
        'views/vendor_dashboard.xml',
        'views/vendor_income_page.xml',
        'views/vendor_product_list.xml',
        'views/vendor_add_product.xml',
        'views/vendor_edit_product.xml',
        'views/vendor_order_list.xml',
        'views/vendor_order_detail.xml',
        'views/vendor_settings.xml',
        'views/wishlist_page.xml',
        'views/checkout_steps.xml',
        'wizard/vendor_refuse_view.xml',
        'wizard/generate_commissions_wizard_view.xml',
    ],
    
    'assets': {
        'web.assets_frontend': [
            'marketplace_platform/static/src/scss/aura_style.scss',
            'marketplace_platform/static/src/js/wishlist.js',
        ],
    },

    'installable': True,
    'application': True, 
    'auto_install': False,
}