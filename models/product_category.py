# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'
    
    # Use fields.Image for better handling
    category_logo = fields.Image(string='Category Logo', max_width=512, height=512)
    
    # Banner image usually needs to be high res, so we define max_width
    banner_image = fields.Image(string='Banner Image', max_width=1920)
    
    seo_description = fields.Text(string='SEO Description')
    is_featured = fields.Boolean(string='Featured Category', default=False)
    
    icon_class = fields.Char(string='Icon Class', help='Font Awesome icon class (e.g., fa-laptop)')