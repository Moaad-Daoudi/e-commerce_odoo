# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import ensure_db
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import werkzeug

class AuraAuth(AuthSignupHome):
    
    # 1. Custom Login Route
    @http.route('/login', type='http', auth='public', website=True, sitemap=False, methods=['GET', 'POST'])
    def aura_login(self, redirect=None, **kw):
        ensure_db()
        
        # If already logged in, go home
        if request.session.uid:
            return request.redirect(redirect or '/')
        
        # Prepare values for template
        values = {
            'login': kw.get('login', ''),
            'redirect': redirect or '/',
            'error': None
        }
        
        # Handle POST (login attempt)
        if request.httprequest.method == 'POST':
            try:
                login = kw.get('login')
                password = kw.get('password')
                
                if not login or not password:
                    values['error'] = 'Please enter both email and password'
                    return request.render("marketplace_platform.login_page", values)
                
                # Try to authenticate
                old_uid = request.uid
                uid = request.session.authenticate(request.db, login, password)
                
                if uid is not False:
                    # Login successful, redirect
                    return request.redirect(redirect or '/')
                else:
                    values['error'] = 'Wrong email or password'
                    return request.render("marketplace_platform.login_page", values)
                    
            except Exception as e:
                error_msg = str(e)
                if 'credentials' in error_msg.lower() or 'authentication' in error_msg.lower():
                    error_msg = 'Wrong email or password'
                values['error'] = error_msg
                return request.render("marketplace_platform.login_page", values)
        
        # Handle GET (show form)
        return request.render("marketplace_platform.login_page", values)

    # 2. Custom Signup Route
    @http.route('/signup', type='http', auth='public', website=True, sitemap=False, methods=['GET', 'POST'])
    def aura_signup(self, *args, **kw):
        ensure_db()
        
        # If already logged in, redirect to home
        if request.session.uid:
            return request.redirect(kw.get('redirect', '/'))
        
        # Prepare values for template
        values = {
            'name': kw.get('name', ''),
            'login': kw.get('login', ''),
            'token': kw.get('token', ''),
            'redirect': kw.get('redirect', '/'),
            'error': None
        }
        
        # Handle POST request (form submission)
        if request.httprequest.method == 'POST':
            try:
                # Get form data
                name = kw.get('name', '').strip()
                login = kw.get('login', '').strip()
                password = kw.get('password', '')
                confirm_password = kw.get('confirm_password', '')
                
                # Validate required fields
                if not name:
                    values['error'] = 'Name is required'
                    return request.render("marketplace_platform.signup_page", values)
                
                if not login:
                    values['error'] = 'Email is required'
                    return request.render("marketplace_platform.signup_page", values)
                
                if not password:
                    values['error'] = 'Password is required'
                    return request.render("marketplace_platform.signup_page", values)
                
                if password != confirm_password:
                    values['error'] = 'Passwords do not match'
                    return request.render("marketplace_platform.signup_page", values)
                
                # Check if user already exists
                existing_user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
                if existing_user:
                    values['error'] = 'This email is already registered. Please login instead.'
                    return request.render("marketplace_platform.signup_page", values)
                
                # Create new user with proper groups
                portal_group = request.env.ref('base.group_portal')
                public_user_group = request.env.ref('base.group_public')
                customer_group = request.env.ref('marketplace_platform.group_marketplace_customer', raise_if_not_found=False)
                
                group_ids = [portal_group.id]
                if customer_group:
                    group_ids.append(customer_group.id)
                
                # Create partner first
                partner = request.env['res.partner'].sudo().create({
                    'name': name,
                    'email': login,
                })
                
                # Create user with proper settings
                user = request.env['res.users'].sudo().create({
                    'login': login,
                    'name': name,
                    'partner_id': partner.id,
                    'password': password,
                    'groups_id': [(6, 0, group_ids)],
                    'active': True,
                })
                
                # Commit the transaction to ensure user is saved
                request.env.cr.commit()
                
                # Auto-login the new user
                uid = request.session.authenticate(request.db, login, password)
                
                if uid:
                    # Login successful, redirect to home
                    return request.redirect(values['redirect'])
                else:
                    values['error'] = 'Account created but login failed. Please try logging in manually.'
                    return request.render("marketplace_platform.signup_page", values)
                
            except Exception as e:
                # If signup fails, show error
                error_msg = str(e)
                # Make error message user-friendly
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    error_msg = 'This email is already registered. Please login instead.'
                elif 'database' in error_msg.lower():
                    error_msg = 'Database error. Please try again later.'
                elif 'password' in error_msg.lower():
                    error_msg = 'Password does not meet requirements'
                
                values['error'] = error_msg
                return request.render("marketplace_platform.signup_page", values)
        
        # Handle GET request (show form)
        return request.render("marketplace_platform.signup_page", values)