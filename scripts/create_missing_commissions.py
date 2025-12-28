#!/usr/bin/env python3
"""
Script to create commissions for existing marketplace orders
Run this script from Odoo shell or as a scheduled action
"""

def create_missing_commissions(env):
    """Create commissions for all confirmed marketplace orders that don't have them"""
    
    SaleOrder = env['sale.order']
    Commission = env['marketplace.commission']
    
    # Find all confirmed marketplace orders
    orders = SaleOrder.search([
        ('state', 'in', ['sale', 'done']),
        ('is_marketplace_order', '=', True)
    ])
    
    print(f"Found {len(orders)} marketplace orders")
    
    created_count = 0
    skipped_count = 0
    
    for order in orders:
        print(f"\nProcessing order: {order.name}")
        
        for line in order.order_line:
            if line.vendor_id:
                # Check if commission already exists
                existing = Commission.search([('order_line_id', '=', line.id)], limit=1)
                
                if existing:
                    print(f"  - Line {line.id}: Commission already exists, skipping")
                    skipped_count += 1
                    continue
                
                # Get commission rate
                product_tmpl = line.product_id.product_tmpl_id
                rate = product_tmpl.commission_rate if product_tmpl.commission_rate else line.vendor_id.default_commission_rate
                
                try:
                    # Create commission
                    commission = Commission.create({
                        'vendor_id': line.vendor_id.id,
                        'order_line_id': line.id,
                        'commission_rate': rate,
                        'state': 'confirmed',
                    })
                    
                    print(f"  - Line {line.id}: Created commission {commission.name} - Vendor: {line.vendor_id.shop_name}, Amount: {commission.vendor_amount}")
                    created_count += 1
                    
                except Exception as e:
                    print(f"  - Line {line.id}: ERROR - {str(e)}")
    
    print(f"\n=== Summary ===")
    print(f"Total commissions created: {created_count}")
    print(f"Total commissions skipped: {skipped_count}")
    
    return created_count


# To run this script:
# 1. From Odoo shell:
#    python odoo-bin shell -c odoo.conf -d your_database_name
#    Then run: exec(open('/path/to/this/script.py').read())
#    Then run: create_missing_commissions(env)
#
# 2. Or add as a server action in Odoo UI
