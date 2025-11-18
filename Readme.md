# MARKETPLACE PLATFORM - CAHIER DES CHARGES (Specifications Document)

## 🎯 PROJECT OVERVIEW

- **Project Name:** Multi-Vendor E-Commerce Marketplace Platform
- **Version:** 1.0
- **Platform:** Odoo 17/18 Enterprise
- **Type:** B2B/B2C Marketplace
- **Target:** Suppliers (Vendors) and Customers (End Users)
- **Development Stack:** **Python-Only Backend Development** (Using Odoo's Native Frontend)

---

## 📋 PROJECT SUMMARY (RÉSUMÉ)

### What is this project?

A **Python-based multi-vendor marketplace** built on Odoo where:

- Multiple vendors can register and sell their products
- Customers can browse, purchase from different vendors in a single order
- Platform automatically calculates and manages vendor commissions
- Each vendor has their own dashboard to manage products, orders, and finances
- Administrator has complete control over vendors, products, and platform settings

### Key Features:

1. **Multi-Vendor System** - Unlimited vendors can join and sell
2. **Automated Commission Management** - Platform automatically deducts commission from each sale
3. **Split Order Processing** - Single customer order splits by vendor for fulfillment
4. **Vendor Portal** - Complete dashboard for vendors to manage their business
5. **Customer Portal** - Order tracking, wishlists, reviews, and profile management
6. **Admin Control Panel** - Vendor approval, product moderation, financial management
7. **Payment Integration** - Stripe, PayPal integration for secure payments
8. **Payout System** - Vendors can request payouts of their earnings

### Development Approach:

- ✅ **100% Python Development** - All business logic in Python
- ✅ **No HTML/CSS/JS Coding** - Use Odoo's standard UI components
- ✅ **Extend Odoo Modules** - Inherit from existing Odoo models
- ✅ **Use Odoo ORM** - All database operations through Python ORM
- ✅ **QWeb Templates** - Simple XML configuration for views

---

## 📌 TABLE OF CONTENTS

1.  **Complete Project Structure**
2.  **General Information**
3.  **Odoo Modules Dependencies & Inheritance**
4.  **Functional Specifications by Page/Module**
    - PAGE 1: Home Page
    - PAGE 2: Shop Page (Product Listing)
    - PAGE 3: Product Detail Page
    - PAGE 4: Shopping Cart & Checkout
    - PAGE 5: Customer Account Dashboard
    - PAGE 6: Vendor Storefront Page
    - PAGE 7: Vendor Dashboard (Seller Portal)
    - PAGE 8: Administrator Panel (Backend)
    - PAGE 9: Static Pages (About, Contact, etc.)
5.  **Technical Architecture**
6.  **User Roles & Permissions**
7.  **Performance Requirements**
8.  **Security Requirements**

---

## 1. COMPLETE PROJECT STRUCTURE

### 📁 Full Directory Structure

```
📦 odoo/
└── 📁 addons/
    └── 📁 marketplace_platform/           # Main marketplace module
        ├── 📄 __init__.py                 # Module initialization
        ├── 📄 __manifest__.py             # Module manifest (dependencies, info)
        │
        ├── 📁 models/                     # Python models (business logic)
        │   ├── 📄 __init__.py
        │   │
        │   ├── 📄 vendor.py               # NEW: Vendor profile management
        │   ├── 📄 commission.py           # NEW: Commission tracking
        │   ├── 📄 payout.py              # NEW: Vendor payout requests
        │   │
        │   ├── 📄 product.py              # INHERIT: product.template
        │   ├── 📄 product_category.py     # INHERIT: product.category
        │   ├── 📄 sale_order.py           # INHERIT: sale.order
        │   ├── 📄 sale_order_line.py      # INHERIT: sale.order.line
        │   ├── 📄 account_move.py         # INHERIT: account.move (invoices)
        │   ├── 📄 stock_picking.py        # INHERIT: stock.picking (delivery)
        │   ├── 📄 res_partner.py          # INHERIT: res.partner (customers/vendors)
        │   ├── 📄 payment_transaction.py  # INHERIT: payment.transaction
        │   ├── 📄 website.py              # INHERIT: website
        │   └── 📄 portal.py               # Portal customizations
        │
        ├── 📁 controllers/                # HTTP controllers (routes, APIs)
        │   ├── 📄 __init__.py
        │   ├── 📄 main.py                 # Main website routes
        │   ├── 📄 vendor_portal.py        # Vendor dashboard routes
        │   ├── 📄 customer_portal.py      # Customer portal routes
        │   ├── 📄 shop.py                 # Shop/product listing routes
        │   └── 📄 api.py                  # REST API endpoints (if needed)
        │
        ├── 📁 views/                      # XML view definitions
        │   ├── 📄 vendor_views.xml        # Backend vendor management
        │   ├── 📄 commission_views.xml    # Commission tracking views
        │   ├── 📄 payout_views.xml        # Payout management views
        │   ├── 📄 product_views.xml       # Extended product views
        │   ├── 📄 sale_order_views.xml    # Extended order views
        │   ├── 📄 account_move_views.xml  # Extended invoice views
        │   ├── 📄 res_partner_views.xml   # Extended partner views
        │   ├── 📄 marketplace_menus.xml   # Backend menu structure
        │   └── 📄 dashboard_views.xml     # Dashboard views
        │
        ├── 📁 templates/                  # QWeb templates (frontend)
        │   ├── 📄 portal_templates.xml    # Customer portal templates
        │   ├── 📄 vendor_portal.xml       # Vendor dashboard templates
        │   ├── 📄 vendor_storefront.xml   # Public vendor store page
        │   ├── 📄 shop_templates.xml      # Shop page customizations
        │   ├── 📄 product_templates.xml   # Product detail customizations
        │   ├── 📄 cart_templates.xml      # Cart customizations
        │   ├── 📄 checkout_templates.xml  # Checkout customizations
        │   └── 📄 assets.xml              # CSS/JS assets (if minimal needed)
        │
        ├── 📁 wizards/                    # Wizard models (popup forms)
        │   ├── 📄 __init__.py
        │   ├── 📄 vendor_approval_wizard.py
        │   ├── 📄 payout_wizard.py
        │   ├── 📄 commission_report_wizard.py
        │   └── 📄 bulk_product_wizard.py
        │
        ├── 📁 reports/                    # Report definitions
        │   ├── 📄 vendor_sales_report.xml
        │   ├── 📄 commission_report.xml
        │   ├── 📄 payout_report.xml
        │   ├── 📄 vendor_invoice_template.xml
        │   └── 📄 report_templates.xml
        │
        ├── 📁 security/                   # Access rights & security
        │   ├── 📄 ir.model.access.csv     # Model access rights
        │   ├── 📄 security.xml            # Security groups & rules
        │   └── 📄 record_rules.xml        # Record-level security
        │
        ├── 📁 data/                       # Initial data & demo data
        │   ├── 📄 commission_rates.xml    # Default commission rates
        │   ├── 📄 email_templates.xml     # Email templates
        │   ├── 📄 cron_jobs.xml           # Scheduled actions
        │   ├── 📄 demo_data.xml           # Demo vendors & products
        │   └── 📄 sequence_data.xml       # Number sequences
        │
        ├── 📁 static/                     # Static files (if needed)
        │   ├── 📁 src/
        │   │   ├── 📁 img/               # Images
        │   │   ├── 📁 css/               # Minimal CSS (optional)
        │   │   └── 📁 js/                # Minimal JS (optional)
        │   └── 📁 description/
        │       ├── 📄 icon.png           # Module icon
        │       └── 📄 index.html         # Module description
        │
        ├── 📁 tests/                      # Unit tests
        │   ├── 📄 __init__.py
        │   ├── 📄 test_vendor.py
        │   ├── 📄 test_commission.py
        │   ├── 📄 test_payout.py
        │   └── 📄 test_order_split.py
        │
        └── 📄 README.md                   # Module documentation

```

---

### 📋 File-by-File Breakdown

#### **Root Files**

| File              | Purpose            | Content                                 |
| ----------------- | ------------------ | --------------------------------------- |
| `__init__.py`     | Module entry point | Import models, controllers, wizards     |
| `__manifest__.py` | Module metadata    | Name, version, dependencies, data files |
| `README.md`       | Documentation      | Installation, usage, features           |

---

#### **📁 models/ - Python Business Logic**

| File                     | Type          | Description                                    |
| ------------------------ | ------------- | ---------------------------------------------- |
| `vendor.py`              | **NEW MODEL** | Vendor profiles, store info, approval workflow |
| `commission.py`          | **NEW MODEL** | Commission calculation and tracking            |
| `payout.py`              | **NEW MODEL** | Payout requests and processing                 |
| `product.py`             | **INHERIT**   | Extend `product.template` with vendor fields   |
| `sale_order.py`          | **INHERIT**   | Extend orders with commission, vendor split    |
| `sale_order_line.py`     | **INHERIT**   | Commission per order line                      |
| `account_move.py`        | **INHERIT**   | Invoice commission tracking                    |
| `stock_picking.py`       | **INHERIT**   | Vendor-specific delivery                       |
| `res_partner.py`         | **INHERIT**   | Add vendor flag, commission rate               |
| `payment_transaction.py` | **INHERIT**   | Commission on payments                         |
| `website.py`             | **INHERIT**   | Website customizations                         |
| `portal.py`              | **INHERIT**   | Portal access customizations                   |

**Key Python Patterns:**

```python
# NEW Model
class MarketplaceVendor(models.Model):
    _name = 'marketplace.vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

# INHERIT Model
class ProductTemplate(models.Model):
    _inherit = 'product.template'
```

---

#### **📁 controllers/ - HTTP Routes**

| File                 | Purpose            | Routes                                                    |
| -------------------- | ------------------ | --------------------------------------------------------- |
| `main.py`            | Main routes        | Home page, general routes                                 |
| `vendor_portal.py`   | Vendor dashboard   | `/vendor/dashboard`, `/vendor/products`, `/vendor/orders` |
| `customer_portal.py` | Customer portal    | `/my/account`, `/my/orders`, `/my/wishlist`               |
| `shop.py`            | Shop functionality | `/shop`, `/shop/vendor/<id>`                              |
| `api.py`             | API endpoints      | REST API for external integrations                        |

**Controller Example:**

```python
class VendorPortal(http.Controller):
    @http.route('/vendor/dashboard', type='http', auth='user', website=True)
    def vendor_dashboard(self, **kwargs):
        # Logic here
        return request.render('marketplace_platform.vendor_dashboard', values)
```

---

#### **📁 views/ - Backend Views (XML)**

| File                    | Purpose                                   |
| ----------------------- | ----------------------------------------- |
| `vendor_views.xml`      | Form, tree, kanban views for vendors      |
| `commission_views.xml`  | Commission tracking views                 |
| `payout_views.xml`      | Payout request management                 |
| `product_views.xml`     | Extended product forms with vendor fields |
| `sale_order_views.xml`  | Extended order views                      |
| `marketplace_menus.xml` | Backend menu structure                    |
| `dashboard_views.xml`   | Dashboard widgets                         |

**View Example:**

```xml
<record id="view_vendor_form" model="ir.ui.view">
    <field name="name">marketplace.vendor.form</field>
    <field name="model">marketplace.vendor</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <field name="store_name"/>
                <field name="commission_rate"/>
            </sheet>
        </form>
    </field>
</record>
```

---

#### **📁 templates/ - Frontend Templates (QWeb)**

| File                     | Purpose                           |
| ------------------------ | --------------------------------- |
| `portal_templates.xml`   | Customer portal pages             |
| `vendor_portal.xml`      | Vendor dashboard frontend         |
| `vendor_storefront.xml`  | Public vendor store page          |
| `shop_templates.xml`     | Shop page filters, vendor display |
| `product_templates.xml`  | Product detail vendor info        |
| `cart_templates.xml`     | Multi-vendor cart display         |
| `checkout_templates.xml` | Checkout customizations           |

**Template Example:**

```xml
<template id="vendor_dashboard_template" name="Vendor Dashboard">
    <t t-call="website.layout">
        <div class="container">
            <h1>Vendor Dashboard</h1>
            <t t-foreach="orders" t-as="order">
                <div t-esc="order.name"/>
            </t>
        </div>
    </t>
</template>
```

---

#### **📁 wizards/ - Popup Forms**

| File                          | Purpose                            |
| ----------------------------- | ---------------------------------- |
| `vendor_approval_wizard.py`   | Approve/reject vendor applications |
| `payout_wizard.py`            | Process payout requests            |
| `commission_report_wizard.py` | Generate commission reports        |
| `bulk_product_wizard.py`      | Bulk product operations            |

---

#### **📁 reports/ - PDF Reports**

| File                          | Purpose                    |
| ----------------------------- | -------------------------- |
| `vendor_sales_report.xml`     | Vendor sales report PDF    |
| `commission_report.xml`       | Commission summary report  |
| `payout_report.xml`           | Payout statement           |
| `vendor_invoice_template.xml` | Custom invoice for vendors |

---

#### **📁 security/ - Access Control**

| File                  | Purpose                                          |
| --------------------- | ------------------------------------------------ |
| `ir.model.access.csv` | Model-level access (CRUD permissions)            |
| `security.xml`        | User groups definition                           |
| `record_rules.xml`    | Record-level rules (vendors see only their data) |

**Access Rights Example:**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_vendor_user,vendor.user,model_marketplace_vendor,group_vendor_user,1,1,1,0
```

---

#### **📁 data/ - Initial Data**

| File                   | Purpose                                |
| ---------------------- | -------------------------------------- |
| `commission_rates.xml` | Default commission percentages         |
| `email_templates.xml`  | Automated email templates              |
| `cron_jobs.xml`        | Scheduled tasks (auto-commission calc) |
| `demo_data.xml`        | Sample vendors and products            |
| `sequence_data.xml`    | Number sequences (ORD001, PAY001)      |

---

### 🎯 Development Workflow

1. **Start with Models** (`models/`)

   - Create NEW models (vendor, commission, payout)
   - Inherit existing models (product, sale.order)

2. **Add Backend Views** (`views/`)

   - Create forms, trees, kanbans
   - Add menus

3. **Set Security** (`security/`)

   - Define user groups
   - Set access rights

4. **Create Controllers** (`controllers/`)

   - Add routes for portals
   - Create APIs

5. **Build Frontend** (`templates/`)

   - Customize website templates
   - Add portal pages

6. **Add Reports** (`reports/`)

   - Generate PDFs
   - Create dashboards

7. **Test** (`tests/`)
   - Write unit tests
   - Test workflows

---

## 2. GENERAL INFORMATION

### 1.1 Project Objectives

- Créer une plateforme marketplace multi-vendeurs évolutive **utilisant uniquement Python**.
- Permettre aux fournisseurs de vendre leurs produits directement aux clients.
- Fournir des outils de gestion complets pour les administrateurs.
- Assurer un traitement sécurisé des paiements et une gestion des commissions.
- Développer toute la logique métier en Python avec Odoo ORM.
- Utiliser les composants frontend standards d'Odoo (pas de développement HTML/CSS/JS personnalisé).

### 1.2 Target Users

- **Platform Administrator:** Gère l'ensemble de la marketplace.
- **Vendors/Suppliers:** Vendent des produits et gèrent leurs boutiques.
- **Customers:** Parcourent et achètent des produits.
- **Guest Users:** Parcourent les produits sans inscription.

### 1.3 Key Business Requirements

- Support pour un nombre illimité de vendeurs et de produits.
- Calcul et versements automatisés des commissions.
- Support multi-devises et multi-langues.
- Suivi des commandes en temps réel et notifications.
- Analyses et rapports complets.

---

## 2. ODOO MODULES DEPENDENCIES & INHERITANCE

### 2.1 Required Odoo Standard Modules (Dependencies)

Your marketplace module will **depend on** and **extend** these existing Odoo modules:

#### **Core Dependencies:**

```python
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
]
```

### 2.2 Modules to Extend/Inherit From

You will **inherit and extend** models from these modules:

#### 📦 **From `product` module:**

- **Model to inherit:** `product.template`, `product.product`
- **What you'll add:**
  - `vendor_id` (Many2one to res.partner)
  - `commission_rate` (Float)
  - `vendor_sku` (Char)
  - `approval_state` (Selection: draft, pending, approved, rejected)

```python
class MarketplaceProduct(models.Model):
    _inherit = 'product.template'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    commission_rate = fields.Float(string='Commission %', default=15.0)
    approval_state = fields.Selection([...])
```

#### 🛒 **From `sale` module:**

- **Model to inherit:** `sale.order`, `sale.order.line`
- **What you'll add:**
  - Split orders by vendor
  - Commission calculation per line
  - Vendor-specific order states
  - Multi-vendor order processing

```python
class MarketplaceSaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    commission_amount = fields.Float(compute='_compute_commission')
    is_marketplace_order = fields.Boolean(default=True)
```

#### 📋 **From `account` module:**

- **Model to inherit:** `account.move` (Invoices)
- **What you'll add:**
  - Vendor commission tracking on invoices
  - Split invoice generation for multi-vendor orders
  - Vendor payout reconciliation

```python
class MarketplaceInvoice(models.Model):
    _inherit = 'account.move'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    commission_amount = fields.Float(string='Platform Commission')
    vendor_net_amount = fields.Float(compute='_compute_vendor_net')
```

#### 📦 **From `stock` module:**

- **Model to inherit:** `stock.picking`, `stock.move`
- **What you'll add:**
  - Vendor-specific delivery tracking
  - Multi-vendor shipment management
  - Vendor inventory control

```python
class MarketplaceStockPicking(models.Model):
    _inherit = 'stock.picking'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    marketplace_order = fields.Boolean(default=False)
```

#### 👤 **From `portal` module:**

- **Model to inherit:** `portal.mixin`
- **What you'll add:**
  - Vendor portal views
  - Custom portal dashboards
  - Vendor-specific menu items

```python
class VendorPortal(models.Model):
    _name = 'marketplace.vendor'
    _inherit = ['portal.mixin', 'mail.thread']
```

#### 💳 **From `payment` module:**

- **Model to inherit:** `payment.transaction`
- **What you'll add:**
  - Commission deduction during payment
  - Vendor payout tracking
  - Split payment logic

#### 🌐 **From `website_sale` module:**

- **Model to inherit:** `website`
- **What you'll add:**
  - Vendor filtering on shop page
  - Vendor storefront pages
  - Multi-vendor cart management

### 2.3 New Custom Models (Not Inherited)

You will **create** these NEW models from scratch:

#### 1️⃣ **Vendor Profile** (`marketplace.vendor`)

```python
class MarketplaceVendor(models.Model):
    _name = 'marketplace.vendor'
    _description = 'Marketplace Vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one('res.partner', required=True)
    store_name = fields.Char(required=True)
    store_url = fields.Char()
    commission_rate = fields.Float(default=15.0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended')
    ])
```

#### 2️⃣ **Commission Tracking** (`marketplace.commission`)

```python
class MarketplaceCommission(models.Model):
    _name = 'marketplace.commission'
    _description = 'Commission Tracking'

    order_id = fields.Many2one('sale.order')
    vendor_id = fields.Many2one('res.partner')
    commission_amount = fields.Float()
    commission_rate = fields.Float()
    sale_amount = fields.Float()
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('paid', 'Paid')])
```

#### 3️⃣ **Vendor Payout** (`marketplace.payout`)

```python
class MarketplacePayout(models.Model):
    _name = 'marketplace.payout'
    _description = 'Vendor Payout Requests'

    vendor_id = fields.Many2one('res.partner', required=True)
    amount = fields.Float(required=True)
    request_date = fields.Date(default=fields.Date.today)
    payment_date = fields.Date()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected')
    ])
```

### 2.4 Module Structure Summary

```
📁 marketplace_platform/
├── 📄 __manifest__.py          # Dependencies declaration
├── 📁 models/
│   ├── vendor.py               # NEW model
│   ├── commission.py           # NEW model
│   ├── payout.py              # NEW model
│   ├── product.py             # INHERITS product.template
│   ├── sale_order.py          # INHERITS sale.order
│   ├── account_move.py        # INHERITS account.move
│   ├── stock_picking.py       # INHERITS stock.picking
│   └── portal.py              # INHERITS portal.mixin
├── 📁 views/
│   ├── vendor_views.xml       # Backend views for vendors
│   ├── product_views.xml      # Extended product views
│   └── portal_templates.xml   # Frontend portal templates
└── 📁 security/
    └── ir.model.access.csv    # Access rights
```

### 2.5 Key Python Patterns You'll Use

#### **Inheritance Pattern:**

```python
# Extending existing models
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    # Add your fields here
```

#### **Compute Fields Pattern:**

```python
commission_amount = fields.Float(compute='_compute_commission')

@api.depends('order_line.price_subtotal')
def _compute_commission(self):
    for order in self:
        order.commission_amount = sum(
            line.price_subtotal * (line.commission_rate / 100)
            for line in order.order_line
        )
```

#### **Override Methods Pattern:**

```python
@api.model
def create(self, vals):
    # Custom logic before create
    result = super().create(vals)
    # Custom logic after create
    return result
```

---

## 3. FUNCTIONAL SPECIFICATIONS BY PAGE/MODULE

### 🏠 PAGE 1: HOME PAGE (Landing Page)

- **Page URL:** `/` or `/home`
- **Purpose:** Page d'accueil principale qui présente la marketplace, attire les visiteurs et génère des conversions.
- **Target Users:** All users (Guests, Customers, Vendors)

#### Page Sections & Functionalities:

- **Header Section:** Logo, barre de navigation principale (Catégories, Vendeurs), barre de recherche avec auto-complétion, icônes panier/liste de souhaits, connexion/compte utilisateur.
- **Hero Section (Banner):** Carrousel de bannières promotionnelles avec des appels à l'action clairs.
- **Features/Benefits Section:** Icônes mettant en avant les avantages clés (Livraison Gratuite, Paiement Sécurisé, etc.).
- **Categories Section:** Grille visuelle des principales catégories de produits.
- **Featured Products Section:** Carrousel de produits mis en avant (meilleures ventes, nouveautés).
- **Flash Sale / Deals Section:** Section avec un compte à rebours pour les offres à durée limitée.
- **Top Vendors Section:** Grille présentant les vendeurs les mieux notés ou les plus populaires.
- **Testimonials/Reviews Section:** Carrousel d'avis clients pour renforcer la confiance.
- **Newsletter Subscription Section:** Formulaire de capture d'e-mails pour le marketing.
- **Footer Section:** Liens utiles (À propos, FAQ, Politiques), informations de contact, icônes de réseaux sociaux et de paiement.

---

### 🛍️ PAGE 2: SHOP PAGE (Product Listing)

- **Page URL:** `/shop` or `/products`
- **Purpose:** Page principale de navigation des produits avec des capacités de filtrage, de tri et de recherche avancées.
- **Target Users:** All users (Guests, Customers)

#### Page Sections & Functionalities:

- **Filter Sidebar (Left Side):**
  - Filtrer par catégorie, fourchette de prix (slider), marque, vendeur, note, disponibilité, etc.
  - Application des filtres via AJAX (sans rechargement de la page).
- **Product Listing Area (Right Side):**
  - **Toolbar:** Options de tri (popularité, prix, nouveauté), bascule d'affichage (grille/liste), nombre de produits par page.
  - **Product Grid/List:** Cartes de produits affichant l'image, le nom, le vendeur, la note, le prix.
  - Fonctionnalités "Quick View", "Add to Cart", "Add to Wishlist" au survol.
  - Badges (Promo, Nouveau, etc.).
- **Pagination:** Navigation entre les pages de résultats.
- **Compare Products Feature:** Possibilité de sélectionner plusieurs produits pour une comparaison côte à côte.

---

### 📦 PAGE 3: PRODUCT DETAIL PAGE

- **Page URL:** `/product/[product-slug]`
- **Purpose:** Page d'information détaillée sur le produit pour convertir les visiteurs en acheteurs.
- **Target Users:** All users (Guests, Customers)

#### Page Sections & Functionalities:

- **Product Images Section (Left Side):**
  - Image principale avec fonction de zoom.
  - Galerie de vignettes pour les images supplémentaires, vidéos, et vue à 360°.
- **Product Information Section (Right Side):**
  - Nom du produit, SKU, marque.
  - Informations sur le vendeur (nom, note, lien vers la boutique).
  - Résumé des avis et de la note moyenne.
  - Prix (avec ancien prix barré si en promotion).
  - Disponibilité du stock.
  - **Sélecteurs de variantes** (taille, couleur, etc.) qui mettent à jour l'image, le prix et le stock.
  - Sélecteur de quantité.
  - Boutons "Ajouter au Panier" et "Acheter Maintenant".
- **Product Tabs Section (Below Main Info):**
  - **Description:** Description complète et détaillée.
  - **Spécifications:** Tableau des caractéristiques techniques.
  - **Avis:** Section complète des avis clients avec filtres et formulaire pour soumettre un avis.
  - **Informations Vendeur:** Profil détaillé du vendeur.
  - **Politiques:** Informations sur la livraison et les retours.
- **Related Products Section:** Carrousels "Vous pourriez également aimer" et "Fréquemment achetés ensemble".

---

### 🛒 PAGE 4: SHOPPING CART & CHECKOUT FLOW

#### 4.1 Page du Panier d'Achat

- **Page URL:** `/cart`
- **Purpose:** Permettre aux utilisateurs de voir, modifier et gérer les produits avant de passer à la caisse.
- **Target Users:** Customers

##### **Page Sections & Functionalities:**

- **Product List:** Liste des articles avec image, nom, vendeur, prix, et sélecteur de quantité.
- **Order Summary:** Sous-total, champ pour code promo, estimation des frais de port et des taxes, total général.
- **Actions:** Boutons "Passer à la Caisse" et "Continuer les Achats".

#### 4.2 Processus de Paiement (Checkout)

- **Page URL:** `/checkout`
- **Purpose:** Collecter les informations de livraison, de facturation et de paiement pour finaliser la commande.
- **Target Users:** Customers

##### **Checkout Steps (One-Page Layout):**

1.  **Login / Guest Checkout:** Option de connexion, d'inscription ou de commande en tant qu'invité.
2.  **Shipping Information:** Formulaire d'adresse de livraison avec autocomplétion et sélection de la méthode d'envoi.
3.  **Payment Information:** Sélection de la méthode de paiement (Carte de crédit, PayPal) via une intégration sécurisée.
4.  **Review & Place Order:** Récapitulatif final de la commande avant confirmation et paiement.

#### 4.3 Page de Confirmation de Commande

- **Page URL:** `/order/success/[order-id]`
- **Purpose:** Confirmer la commande et fournir les prochaines étapes.
- **Components:** Message de remerciement, numéro de commande, résumé, date de livraison estimée, lien de suivi.

---

### 👤 PAGE 5: CUSTOMER ACCOUNT DASHBOARD

- **Page URL:** `/account/*`
- **Purpose:** Permettre aux clients de gérer leurs informations personnelles, commandes, et activités.
- **Target Users:** Customers

##### **Dashboard Sections & Functionalities:**

- **Mes Commandes:** Historique des commandes avec suivi, détails et options de retour/avis.
- **Mon Profil:** Modifier les informations personnelles et le mot de passe.
- **Adresses:** Gérer un carnet d'adresses de livraison et de facturation.
- **Liste de Souhaits:** Gérer les produits sauvegardés.
- **Mes Avis:** Voir les avis soumis et les produits en attente d'avis.

---

### 🏪 PAGE 6: VENDOR STOREFRONT PAGE

- **Page URL:** `/vendor/[vendor-slug]`
- **Purpose:** Page publique pour chaque vendeur, présentant leur marque, produits et évaluations.
- **Target Users:** All Users

##### **Page Sections & Functionalities:**

- **Header de la Boutique:** Bannière, logo, nom du vendeur, note moyenne.
- **Navigation:** Onglets (Accueil, Produits, Avis, Politiques, À Propos).
- **Product Listing:** Grille de tous les produits du vendeur avec des filtres spécifiques à la boutique.

---

### 📈 PAGE 7: VENDOR DASHBOARD (SELLER PORTAL)

- **Page URL:** `/vendor/dashboard`
- **Purpose:** Le centre de contrôle complet pour les vendeurs pour gérer leur boutique.
- **Target Users:** Vendors

##### **Dashboard Sections & Functionalities:**

- **Tableau de Bord:** Vue d'ensemble des ventes, des commandes et des statistiques.
- **Gestion des Produits:** Ajouter, modifier, supprimer des produits, gérer les stocks et les variantes. Import/export en masse.
- **Gestion des Commandes:** Traiter les commandes, ajouter des informations de suivi, communiquer avec les clients.
- **Finances & Versements:** Suivre les gains, les commissions et demander des versements.
- **Rapports & Analyses:** Rapports sur les ventes, les produits les plus performants.
- **Paramètres de la Boutique:** Personnaliser l'apparence de la boutique et définir les politiques d'expédition/retour.

---

### ⚙️ PAGE 8: ADMINISTRATOR PANEL (BACKEND)

- **Page URL:** `/admin`
- **Purpose:** Interface de gestion centrale pour l'administrateur de la plateforme.
- **Target Users:** Platform Administrator

##### **Admin Panel Sections & Functionalities:**

- **Gestion des Vendeurs:** Approuver, suspendre, gérer les vendeurs et définir les taux de commission.
- **Gestion des Produits:** Superviser le catalogue global et approuver les soumissions de produits.
- **Gestion des Commandes:** Vue globale de toutes les commandes et gestion des litiges.
- **Gestion Financière:** Suivre les commissions, gérer les versements.
- **Gestion du Contenu du Site (CMS):** Gérer la page d'accueil et les pages statiques.
- **Marketing & Promotions:** Créer des promotions à l'échelle du site.
- **Paramètres du Système:** Configurer les paiements, les taxes, les langues, etc.

---

## 3. TECHNICAL ARCHITECTURE

### 3.1 Development Approach: **PYTHON-ONLY BACKEND**

- **NO custom HTML, CSS, or JavaScript development required**
- **All functionality implemented using Python and Odoo framework**
- Uses Odoo's standard views and templates (QWeb)
- Customizations done through Python models, views, and controllers

### 3.2 Technology Stack

#### **Backend (Primary Focus):**

- **Language:** Python 3.10+
- **Framework:** Odoo 17/18 Enterprise Edition
- **ORM:** Odoo ORM (Object-Relational Mapping)
- **Database:** PostgreSQL 14+
- **Server:** Odoo WSGI/ASGI server

#### **Frontend (Standard Odoo):**

- **Templates:** QWeb (XML-based templating engine)
- **Framework:** Odoo's native website builder
- **UI Components:** Standard Odoo website/eCommerce modules
- **No custom frontend development** - All UI through Odoo's standard components

#### **Python Modules Structure:**

```
odoo/addons/marketplace_platform/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── vendor.py
│   ├── marketplace_product.py
│   ├── marketplace_order.py
│   ├── commission.py
│   └── payout.py
├── controllers/
│   ├── __init__.py
│   ├── portal.py
│   └── vendor_portal.py
├── views/
│   ├── vendor_views.xml
│   ├── product_views.xml
│   ├── order_views.xml
│   └── portal_templates.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── demo_data.xml
└── reports/
    └── vendor_reports.xml
```

#### **Infrastructure:**

- **Hosting:** Cloud-based (AWS, Google Cloud, Azure) or on-premise
- **Database:** PostgreSQL with automated backups
- **Caching:** Redis (if needed for performance)

#### **Python APIs & Integrations:**

- **Payment:** Python SDK for Stripe, PayPal, Adyen
- **Shipping:** Python API clients for DHL, FedEx, etc.
- **Email:** Odoo's built-in email system
- **Reports:** Odoo's Python-based reporting engine

### 3.3 Python Development Focus Areas

#### **Core Python Models:**

1. **Vendor Management** (`models/vendor.py`)

   - Vendor registration and approval
   - Store configuration
   - Commission rates

2. **Product Management** (`models/marketplace_product.py`)

   - Multi-vendor product catalog
   - Inventory management
   - Product variants

3. **Order Processing** (`models/marketplace_order.py`)

   - Split orders by vendor
   - Order workflow and state management
   - Automated notifications

4. **Commission System** (`models/commission.py`)

   - Automatic commission calculation
   - Commission tracking per order
   - Financial reports

5. **Payout Management** (`models/payout.py`)
   - Vendor earnings calculation
   - Payout requests and processing
   - Payment reconciliation

#### **Python Controllers:**

- Portal controllers for customer/vendor interfaces
- API endpoints for external integrations
- Webhook handlers for payment providers

#### **Business Logic (Pure Python):**

- All business rules in Python code
- Automated workflows using Python
- Scheduled actions (cron jobs) in Python
- Email templates with Python variables

---

## 4. USER ROLES & PERMISSIONS

- **Guest:** Peut naviguer et ajouter au panier.
- **Customer:** Peut acheter, gérer son compte, laisser des avis.
- **Vendor:** Accès au tableau de bord vendeur pour gérer sa propre boutique, ses produits et ses commandes.
- **Administrator:** Accès complet à toutes les fonctionnalités de gestion de la plateforme.

### 4.1 PAGE ACCESS MATRIX BY ROLE

#### 🚶 **GUEST USER** (Not Logged In)

- ✅ **PAGE 1:** Home Page - Full access
- ✅ **PAGE 2:** Shop Page (Product Listing) - Full access
- ✅ **PAGE 3:** Product Detail Page - Full access
- ✅ **PAGE 4:** Shopping Cart - Can view and add items
- ❌ **PAGE 4:** Checkout - Must login/register to complete purchase
- ❌ **PAGE 5:** Customer Account Dashboard - Must login to access
- ✅ **PAGE 6:** Vendor Storefront Page - Full access (view only)
- ❌ **PAGE 7:** Vendor Dashboard - Not accessible
- ❌ **PAGE 8:** Administrator Panel - Not accessible
- ✅ **PAGE 9:** Static Pages (About, Contact, FAQ, Terms) - Full access

#### 👤 **CUSTOMER** (Registered User)

- ✅ **PAGE 1:** Home Page - Full access
- ✅ **PAGE 2:** Shop Page (Product Listing) - Full access
- ✅ **PAGE 3:** Product Detail Page - Full access + Can leave reviews
- ✅ **PAGE 4:** Shopping Cart & Checkout - Full access
- ✅ **PAGE 5:** Customer Account Dashboard - Full access
  - `/account/dashboard` - Overview
  - `/account/orders` - Order history and tracking
  - `/account/profile` - Edit personal information
  - `/account/addresses` - Manage shipping/billing addresses
  - `/account/wishlist` - Manage saved products
  - `/account/reviews` - Manage product reviews
- ✅ **PAGE 6:** Vendor Storefront Page - Full access (view + follow vendors)
- ❌ **PAGE 7:** Vendor Dashboard - Not accessible (unless also a vendor)
- ❌ **PAGE 8:** Administrator Panel - Not accessible
- ✅ **PAGE 9:** Static Pages - Full access

#### 🏪 **VENDOR** (Seller)

- ✅ **PAGE 1:** Home Page - Full access
- ✅ **PAGE 2:** Shop Page (Product Listing) - Full access
- ✅ **PAGE 3:** Product Detail Page - Full access
- ✅ **PAGE 4:** Shopping Cart & Checkout - Full access (can also purchase)
- ✅ **PAGE 5:** Customer Account Dashboard - Full access (if also a customer)
- ✅ **PAGE 6:** Vendor Storefront Page - Full access (own store + others)
- ✅ **PAGE 7:** Vendor Dashboard (Seller Portal) - **FULL ACCESS**
  - `/vendor/dashboard` - Sales overview and statistics
  - `/vendor/products` - Product management (CRUD operations)
  - `/vendor/products/add` - Add new products
  - `/vendor/products/import` - Bulk product import
  - `/vendor/orders` - Order management and fulfillment
  - `/vendor/finances` - Earnings, commissions, payout requests
  - `/vendor/reports` - Sales reports and analytics
  - `/vendor/settings` - Store customization and policies
  - `/vendor/profile` - Vendor profile and business information
- ❌ **PAGE 8:** Administrator Panel - Not accessible
- ✅ **PAGE 9:** Static Pages - Full access

#### ⚙️ **ADMINISTRATOR** (Platform Admin)

- ✅ **PAGE 1:** Home Page - Full access + Edit capabilities
- ✅ **PAGE 2:** Shop Page (Product Listing) - Full access + Management tools
- ✅ **PAGE 3:** Product Detail Page - Full access + Moderation tools
- ✅ **PAGE 4:** Shopping Cart & Checkout - Full access
- ✅ **PAGE 5:** Customer Account Dashboard - Can view all customer accounts
- ✅ **PAGE 6:** Vendor Storefront Page - Full access + Moderation
- ✅ **PAGE 7:** Vendor Dashboard - Can access any vendor dashboard
- ✅ **PAGE 8:** Administrator Panel (Backend) - **FULL ACCESS**
  - `/admin/dashboard` - Platform overview and metrics
  - `/admin/vendors` - Vendor approval, management, suspension
  - `/admin/products` - Global product catalog oversight
  - `/admin/orders` - All orders management
  - `/admin/customers` - Customer management
  - `/admin/finances` - Commission tracking and payout management
  - `/admin/cms` - Content management (homepage, banners, pages)
  - `/admin/marketing` - Promotions and campaigns
  - `/admin/settings` - Platform configuration (payments, taxes, shipping)
  - `/admin/reports` - Comprehensive analytics and reporting
  - `/admin/security` - User permissions and security settings
- ✅ **PAGE 9:** Static Pages - Full access + Edit capabilities

---

## 5. PERFORMANCE REQUIREMENTS

- **Temps de chargement des pages:** < 3 secondes.
- **Temps de réponse du serveur (TTFB):** < 300ms.
- **Disponibilité:** 99.9% de temps de fonctionnement.
- **Concurrence:** Doit supporter un grand nombre d'utilisateurs simultanés sans dégradation.
- **Optimisation:** Scores Google PageSpeed Insights > 85/100.

---

## 6. SECURITY REQUIREMENTS

- **Chiffrement:** HTTPS (SSL/TLS) sur l'ensemble du site.
- **Sécurité des mots de passe:** Hachage robuste des mots de passe.
- **Protection des données:** Conformité avec le RGPD.
- **Sécurité des paiements:** Conformité totale à la norme PCI DSS.
- **Prévention des attaques:** Protection contre les vulnérabilités de l'OWASP Top 10 (injection SQL, XSS, CSRF).
- **Sauvegardes:** Sauvegardes régulières et automatisées de la base de données.
