// Library Management System - Client-side JavaScript

// Confirm dialog before borrow request
function confirmBorrow() {
    return confirm('Are you sure you want to borrow this book?');
}

// Confirm dialog before return
function confirmReturn() {
    return confirm('Are you sure you want to return this book?');
}

// Form validation - prevent empty field submission
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    if (!isValid) {
        alert('Please fill in all required fields.');
    }
    
    return isValid;
}

// Live search filtering (client-side)
function liveSearchBooks() {
    const searchInput = document.querySelector('input[name="query"]');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const bookItems = document.querySelectorAll('.book-item');
        
        bookItems.forEach(item => {
            const title = item.getAttribute('data-title');
            const author = item.getAttribute('data-author');
            
            if (title.includes(searchTerm) || author.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// Highlight overdue books dynamically
function highlightOverdueBooks() {
    const overdueRows = document.querySelectorAll('.overdue-row');
    overdueRows.forEach(row => {
        row.style.backgroundColor = '#f8d7da';
        row.style.fontWeight = 'bold';
    });
}

// Auto-dismiss alerts after 5 seconds
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Add loading indicator for forms
function addLoadingIndicator(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function() {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        }
    });
}

// Validate date inputs
function validateDateInput(inputId, minDate) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('change', function() {
        const selectedDate = new Date(this.value);
        const min = minDate ? new Date(minDate) : new Date();
        
        if (selectedDate < min) {
            alert('Please select a future date.');
            this.value = '';
        }
    });
}

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top button
function addScrollToTopButton() {
    const button = document.createElement('button');
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3';
    button.style.display = 'none';
    button.style.zIndex = '1000';
    button.onclick = scrollToTop;
    
    document.body.appendChild(button);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
    });
}

// Confirm before approving/rejecting borrow requests
function confirmAction(action, bookTitle) {
    return confirm(`Are you sure you want to ${action} the borrow request for "${bookTitle}"?`);
}

// Real-time search suggestions
function setupSearchSuggestions() {
    const searchInput = document.querySelector('input[name="query"]');
    if (!searchInput) return;
    
    let timeout = null;
    searchInput.addEventListener('input', function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            // This would connect to a backend endpoint for suggestions
            // For now, just highlight matching items
            liveSearchBooks();
        }, 300);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functions
    highlightOverdueBooks();
    autoDismissAlerts();
    initializeTooltips();
    liveSearchBooks();
    setupSearchSuggestions();
    addScrollToTopButton();
    
    // Add loading indicators to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.id) {
            addLoadingIndicator(form.id);
        }
    });
    
    // Validate date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        validateDateInput(input.id, new Date());
    });
    
    // Add confirmation to delete actions
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
    
    // Prevent double form submission
    const allForms = document.querySelectorAll('form');
    allForms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                setTimeout(() => {
                    submitBtn.disabled = true;
                }, 0);
            }
        });
    });
});

// Export functions for use in templates
window.confirmBorrow = confirmBorrow;
window.confirmReturn = confirmReturn;
window.validateForm = validateForm;
window.confirmAction = confirmAction;
