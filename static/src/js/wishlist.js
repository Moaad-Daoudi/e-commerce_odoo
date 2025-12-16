// Wishlist notification functionality
(function() {
    'use strict';

    console.log('[Wishlist] JavaScript loaded successfully');

    // Update wishlist button to show filled red heart
    function updateWishlistButton(productId) {
        // Find all wishlist buttons for this product
        const buttons = document.querySelectorAll(`[data-product-id="${productId}"]`);
        buttons.forEach(button => {
            const icon = button.querySelector('i');
            if (icon) {
                // Change to filled heart
                icon.className = 'fa fa-heart fs-5';
                icon.style.color = '#dc3545';
                button.classList.add('in-wishlist');
            }
        });
    }

    // Show notification (success or error)
    function showWishlistNotification() {
        // Check if URL has wishlist parameters
        const urlParams = new URLSearchParams(window.location.search);
        console.log('[Wishlist] Checking URL params:', window.location.search);
        
        // Success notification
        if (urlParams.get('wishlist_added') === '1') {
            console.log('[Wishlist] Showing success notification');
            
            // Create notification element
            const notification = document.createElement('div');
            notification.className = 'wishlist-success-notification';
            notification.innerHTML = '<i class="fa fa-heart text-danger"></i> Added to wishlist!';
            document.body.appendChild(notification);

            // Show notification
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);

            // Hide after 3 seconds
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 3000);

            // Update all wishlist buttons on the page to show filled heart
            // Get product ID from current page or URL
            const pathParts = window.location.pathname.split('/');
            if (pathParts.includes('product')) {
                const productIndex = pathParts.indexOf('product');
                if (pathParts[productIndex + 1]) {
                    updateWishlistButton(pathParts[productIndex + 1]);
                }
            }

            // Remove parameter from URL without reload
            urlParams.delete('wishlist_added');
            const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
            window.history.replaceState({}, '', newUrl);
        }
        
        // Error notification
        if (urlParams.get('wishlist_error') === '1') {
            console.log('[Wishlist] Error occurred');
            const errorMsg = urlParams.get('error') || 'Failed to add to wishlist';
            console.error('[Wishlist] Error message:', errorMsg);
            
            // Create error notification
            const notification = document.createElement('div');
            notification.className = 'wishlist-success-notification';
            notification.style.borderLeft = '4px solid #dc3545';
            notification.style.background = '#fff5f5';
            notification.innerHTML = '<i class="fa fa-exclamation-triangle text-danger"></i> ' + errorMsg;
            document.body.appendChild(notification);

            // Show notification
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);

            // Hide after 5 seconds
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 5000);

            // Remove parameters from URL without reload
            urlParams.delete('wishlist_error');
            urlParams.delete('error');
            const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
            window.history.replaceState({}, '', newUrl);
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showWishlistNotification);
    } else {
        showWishlistNotification();
    }

    // Change heart icon to red on wishlist buttons when hovering
    document.addEventListener('DOMContentLoaded', function() {
        const wishlistButtons = document.querySelectorAll('.btn-wish-float, .btn-wish-outline');
        wishlistButtons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                const icon = this.querySelector('i');
                if (icon) {
                    icon.style.color = '#dc3545';
                }
            });
            button.addEventListener('mouseleave', function() {
                const icon = this.querySelector('i');
                if (icon) {
                    icon.style.color = '';
                }
            });
        });
    });
})();
