# -*- coding: utf-8 -*-
{
    'name': "Marketplace Platform",
    'summary': """
        Plateforme Multi-vendeurs pour Odoo : 
        Gestion des vendeurs, commissions, et séparation des commandes.
    """,

    'description': """
        Marketplace Odoo - Module complet
        =================================
        Ce module transforme Odoo en une place de marché B2B/B2C.
        
        Fonctionnalités principales :
        - Inscription et approbation des vendeurs
        - Gestion des produits par vendeur
        - Split des commandes (une commande client = plusieurs ordres de livraison)
        - Calcul automatique des commissions
        - Gestion des demandes de versement (Payouts)
        - Portail vendeur dédié
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
    ],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/demo_data.xml',
        'views/admin/vendor_views.xml',
        'views/admin/product_views.xml',
        'views/admin/commission_views.xml',
        'views/admin/menu.xml',
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
        'views/login_page.xml',
        'views/signup_page.xml',
        'views/about_page.xml',
        'views/contact_page.xml',
        'views/vendor_registration.xml',
        'views/vendor_dashboard.xml',
        'views/vendor_product_list.xml',
        'views/vendor_add_product.xml',
        'views/vendor_edit_product.xml',
        'views/vendor_order_list.xml',
        'views/vendor_order_detail.xml',
        'views/vendor_settings.xml',
        'views/wishlist_page.xml', 
        'wizard/vendor_refuse_view.xml',
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