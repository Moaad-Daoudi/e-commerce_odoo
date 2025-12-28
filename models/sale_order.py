# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_marketplace_order = fields.Boolean(string="Commande Marketplace", compute='_compute_is_marketplace', store=True)
    
    @api.depends('order_line.vendor_id')
    def _compute_is_marketplace(self):
        for order in self:
            order.is_marketplace_order = any(order.order_line.mapped('vendor_id'))

    def action_confirm(self):
        """ Surcharge de la confirmation pour générer les commissions """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.is_marketplace_order:
                order._create_marketplace_commissions()
        # Delayed picking validation to ensure pickings are created
        for order in self:
            if order.is_marketplace_order and order.picking_ids:
                # Use a deferred job or immediate execution
                order._auto_validate_marketplace_pickings()
        return res
    
    def action_create_commissions_manually(self):
        """ Manual button to create commissions for existing orders """
        for order in self:
            if order.state in ['sale', 'done'] and order.is_marketplace_order:
                order._create_marketplace_commissions()
        return True
    
    def _auto_validate_marketplace_pickings(self):
        """ Automatically validate delivery orders for digital/marketplace products """
        for picking in self.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel']):
            try:
                # Check availability first
                if picking.state in ['confirmed', 'waiting']:
                    picking.action_assign()
                
                # Set quantities done for all moves
                for move in picking.move_ids.filtered(lambda m: m.state not in ['done', 'cancel']):
                    # Set qty_done = product_uom_qty to mark as done
                    move.quantity = move.product_uom_qty
                    
                    # Also set move lines if they exist
                    if move.move_line_ids:
                        for move_line in move.move_line_ids:
                            move_line.quantity = move_line.product_uom_qty
                    else:
                        # Create move line if it doesn't exist
                        move._action_assign()
                        if move.move_line_ids:
                            for move_line in move.move_line_ids:
                                move_line.quantity = move_line.product_uom_qty
                
                # Validate the picking - this reduces stock
                if picking.state in ['assigned', 'confirmed']:
                    # Use button_validate which handles the wizard
                    res = picking.button_validate()
                    
                    # If wizard is returned, process it automatically
                    if isinstance(res, dict) and res.get('res_model') == 'stock.immediate.transfer':
                        immediate_transfer = self.env['stock.immediate.transfer'].browse(res['res_id'])
                        immediate_transfer.process()
                    elif isinstance(res, dict) and res.get('res_model') == 'stock.backorder.confirmation':
                        backorder_confirmation = self.env['stock.backorder.confirmation'].browse(res['res_id'])
                        backorder_confirmation.process()
                        
            except Exception as e:
                # Log error but don't block order confirmation
                self.message_post(
                    body=f"Could not auto-validate delivery: {str(e)}",
                    message_type='comment'
                )

    def _create_marketplace_commissions(self):
        """ Génère les enregistrements de commission pour chaque ligne """
        Commission = self.env['marketplace.commission']
        notified_vendors = set()
        
        for line in self.order_line:
            if line.vendor_id:
                # Check if commission already exists for this line
                existing = Commission.search([('order_line_id', '=', line.id)], limit=1)
                if existing:
                    continue  # Skip if already created
                
                # Get commission rate from product template or vendor
                product_tmpl = line.product_id.product_tmpl_id
                rate = product_tmpl.commission_rate if product_tmpl.commission_rate else line.vendor_id.default_commission_rate
                
                try:
                    # Create commission record
                    commission = Commission.create({
                        'vendor_id': line.vendor_id.id,
                        'order_line_id': line.id,
                        'commission_rate': rate,
                        'state': 'confirmed',  # Set to confirmed when order is confirmed
                    })
                    
                    # Log commission creation
                    self.message_post(
                        body=f"Commission created: {commission.name} for vendor {line.vendor_id.shop_name} - Amount: {commission.vendor_amount}",
                        message_type='comment'
                    )
                    
                    # Notify vendor once per order
                    if line.vendor_id.id not in notified_vendors:
                        notified_vendors.add(line.vendor_id.id)
                        self._notify_vendor_new_order(line.vendor_id)
                except Exception as e:
                    # Log error
                    self.message_post(
                        body=f"Error creating commission for line {line.id}: {str(e)}",
                        message_type='comment'
                    )
    
    def _notify_vendor_new_order(self, vendor):
        """ Send notification to vendor about new order """
        # Post message to vendor's chatter
        vendor.message_post(
            body=f"<p>Nouvelle commande reçue! Commande #{self.name}</p>"
                 f"<p>Client: {self.partner_id.name}</p>"
                 f"<p>Montant: {self.amount_total} {self.currency_id.symbol}</p>",
            subject=f"Nouvelle Commande - {self.name}",
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )
        
        # Also send email notification if vendor has email
        if vendor.email:
            mail_template = self.env.ref('marketplace_platform.email_template_vendor_new_order', raise_if_not_found=False)
            if mail_template:
                mail_template.send_mail(vendor.id, force_send=True)
        
        # Create activity for vendor user
        if vendor.partner_id and vendor.partner_id.user_ids:
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get('marketplace.vendor').id,
                'res_id': vendor.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f'Nouvelle commande: {self.name}',
                'note': f'Une nouvelle commande a été passée pour vos produits.',
                'user_id': vendor.partner_id.user_ids[0].id,
            })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vendor_id = fields.Many2one(
        'marketplace.vendor', 
        related='product_id.product_tmpl_id.vendor_id', 
        string="Vendeur", 
        store=True,
        readonly=True
    )