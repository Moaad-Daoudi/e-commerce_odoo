/** @odoo-module **/

document.addEventListener('DOMContentLoaded', function() {
    // Handle wishlist heart clicks
    document.addEventListener('click', function(e) {
        const heartLink = e.target.closest('a[href*="/wishlist/add/"], a[href*="/wishlist/remove/"]');
        if (!heartLink) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        const href = heartLink.getAttribute('href');
        const icon = heartLink.querySelector('i');
        
        // Show loading
        const originalClass = icon.className;
        const originalColor = icon.style.color;
        icon.className = 'fa fa-spinner fa-spin';
        
        // Make request
        fetch(href, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.redirected || response.ok) {
                // Toggle heart icon
                if (href.includes('/wishlist/add/')) {
                    icon.className = 'fa fa-heart';
                    icon.style.color = '#dc3545';
                    heartLink.href = href.replace('/wishlist/add/', '/wishlist/remove/');
                } else {
                    icon.className = 'fa fa-heart-o';
                    icon.style.color = '';
                    heartLink.href = href.replace('/wishlist/remove/', '/wishlist/add/');
                }
            } else {
                // Restore original if error
                icon.className = originalClass;
                icon.style.color = originalColor;
            }
        })
        .catch(error => {
            console.error('Wishlist error:', error);
            icon.className = originalClass;
            icon.style.color = originalColor;
        });
    });
});
