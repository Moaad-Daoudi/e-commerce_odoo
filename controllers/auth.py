# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import ensure_db, Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

class AuraAuth(AuthSignupHome):
    
    # 1. Custom Login Route
    @http.route('/login', type='http', auth='public', website=True, sitemap=False)
    def aura_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        
        # If already logged in, go home
        if request.session.uid:
            return request.redirect(redirect or '/')
        
        # Get error message if coming from a failed attempt
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
            
        return request.render("marketplace_platform.login_page", values)

    # 2. Custom Signup Route
    @http.route('/signup', type='http', auth='public', website=True, sitemap=False)
    def aura_signup(self, redirect=None, **kw):
        ensure_db()
        
        if request.session.uid:
            return request.redirect(redirect or '/')
            
        values = request.params.copy()
        return request.render("marketplace_platform.signup_page", values)