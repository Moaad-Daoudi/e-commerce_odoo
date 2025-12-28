#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create missing marketplace commissions for existing orders
Run this script to retroactively create commission records
"""

import sys
import os

# Add Odoo to path
sys.path.insert(0, r'C:\Program Files\Odoo 17.0.20251016\server')

import odoo
from odoo import api, SUPERUSER_ID

def create_all_commissions(dbname='Marketplace_1'):
    """Create commissions for all confirmed orders without commission records"""
    
    # Initialize Odoo
    odoo.tools.config.parse_config([
        '-c', r'C:\Program Files\Odoo 17.0.20251016\server\odoo.conf',
        '-d', dbname
    ])
    
    # Connect to database
    registry = odoo.registry(dbname)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True,
            'mail_notrack': True,
            'tracking_disable': True
        })
        
        try:
            # Get all confirmed orders
            orders = env['sale.order'].search([('state', '=', 'sale')])
            print(f"Found {len(orders)} confirmed orders")
            
            # Get existing commissions
            existing_commissions = env['marketplace.commission'].search([])
            print(f"Found {len(existing_commissions)} existing commissions")
            
            # Create commissions for each order
            created_count = 0
            for order in orders:
                # Check if order already has commissions
                order_commissions = existing_commissions.filtered(
                    lambda c: c.order_line_id.order_id.id == order.id
                )
                
                if order_commissions:
                    print(f"  Order {order.name} already has {len(order_commissions)} commissions, skipping")
                    continue
                
                # Create commissions (with email disabled)
                try:
                    order.with_context(
                        mail_create_nosubscribe=True,
                        mail_create_nolog=True,
                        mail_notrack=True
                    )._create_marketplace_commissions()
                    created_count += 1
                    print(f"  ✓ Created commissions for order {order.name}")
                except Exception as e:
                    print(f"  ✗ Error creating commissions for {order.name}: {e}")
                    continue
            
            # Commit all changes
            cr.commit()
            
            # Verify final count
            final_commissions = env['marketplace.commission'].search([])
            print(f"\n{'='*50}")
            print(f"SUCCESS!")
            print(f"Created commissions for {created_count} orders")
            print(f"Total commissions in database: {len(final_commissions)}")
            print(f"{'='*50}")
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            cr.rollback()

if __name__ == '__main__':
    create_all_commissions()
