# -*- coding: utf-8 -*-
from odoo import models, fields, api

class GenerateCommissionsWizard(models.TransientModel):
    _name = 'marketplace.generate.commissions.wizard'
    _description = 'Generate Missing Commissions'

    order_count = fields.Integer(string="Orders Found", readonly=True)
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Count orders that could have commissions
        order_count = self.env['sale.order'].search_count([
            ('state', 'in', ['sale', 'done']),
            ('is_marketplace_order', '=', True)
        ])
        res['order_count'] = order_count
        return res
    
    def action_generate(self):
        """Generate commissions for all confirmed marketplace orders"""
        SaleOrder = self.env['sale.order']
        
        # Find all confirmed marketplace orders
        orders = SaleOrder.search([
            ('state', 'in', ['sale', 'done']),
            ('is_marketplace_order', '=', True)
        ])
        
        # Trigger commission creation
        for order in orders:
            order._create_marketplace_commissions()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Processed {len(orders)} marketplace orders. Check commission records.',
                'sticky': False,
                'type': 'success'
            }
        }
