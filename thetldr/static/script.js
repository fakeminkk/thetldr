function closeMobileMenu() {
    const mobileNav = document.getElementById('mobileNav');
    if (mobileNav) {
        mobileNav.classList.add('-translate-x-full');
    }
}

// Prevent text selection via keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Prevent Ctrl+A (Select All)
    if (e.ctrlKey && e.key === 'a') {
        e.preventDefault();
        return false;
    }
    // Prevent Ctrl+C (Copy) - optional
    // if (e.ctrlKey && e.key === 'c') {
    //     e.preventDefault();
    //     return false;
    // }
});

// Prevent text selection via mouse
document.addEventListener('selectstart', function(e) {
    // Allow selection only in links
    if (e.target.tagName !== 'A') {
        e.preventDefault();
        return false;
    }
});

// Prevent text selection on mouse drag
document.addEventListener('mousedown', function(e) {
    if (e.target.tagName !== 'A') {
        if (window.getSelection) {
            window.getSelection().removeAllRanges();
        }
    }
});

// Clear any existing selection
setInterval(function() {
    if (window.getSelection) {
        const selection = window.getSelection();
        // Only allow selection in links
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;
            if (container.nodeType === 1) {
                // Element node
                if (container.tagName !== 'A' && !container.closest('a')) {
                    selection.removeAllRanges();
                }
            } else {
                // Text node
                if (!container.parentElement || container.parentElement.tagName !== 'A') {
                    selection.removeAllRanges();
                }
            }
        }
    }
}, 100);

// Mobile menu handlers
document.addEventListener('DOMContentLoaded', function() {
    const closeMobileMenuBtn = document.getElementById('closeMobileMenu');
    
    if (closeMobileMenuBtn) {
        closeMobileMenuBtn.addEventListener('click', closeMobileMenu);
    }
    
    // Close menu when clicking outside
    const mobileNav = document.getElementById('mobileNav');
    if (mobileNav) {
        mobileNav.addEventListener('click', function(e) {
            if (e.target === mobileNav) {
                closeMobileMenu();
            }
        });
    }
});

