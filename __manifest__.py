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
    ],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/vendor_views.xml',
        'views/product_views.xml',
        'views/commission_views.xml',
        'views/menu.xml',
        'wizard/vendor_refuse_view.xml',
    ],

    'installable': True,
    'application': True, 
    'auto_install': False,
}