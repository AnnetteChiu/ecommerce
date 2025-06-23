// Main JavaScript file for the Dynamic Content Manager

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Enhanced form validation feedback
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time character count for textareas
    var textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        if (textarea.id === 'content') {
            addCharacterCounter(textarea);
        }
    });
    
    // Auto-save draft functionality (simulate with localStorage)
    var contentForm = document.querySelector('form[action*="create_content"], form[action*="edit_content"]');
    if (contentForm) {
        setupAutoSave(contentForm);
    }
    
    // Enhanced search functionality
    setupAdvancedSearch();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Enhanced dropdown menu hover timing
    setupDropdownHoverTiming();
    
    // Swipe gestures removed per user request
    
    // Initialize floating action button
    initFloatingActionButton();
    
    // Initialize social media sharing
    initSocialMediaSharing();
    
    // Initialize skeleton loading system
    initializeSkeletonLoading();
    
    // Shopping cart shortcuts and quick actions
    setupCartShortcuts();
    
    // Initialize floating cart
    setupFloatingCart();
    
    // Initialize price comparison tooltips
    setupPriceComparison();
    
    // Responsive interactions
    setupResponsiveInteractions();
    
    // Mobile optimization
    setupMobileOptimizations();
    
    // Touch device enhancements
    setupTouchEnhancements();
    
    // Swipe gestures removed per user request
    
    // Initialize micro-interactions and animations
    initializeMicroInteractions();
    
    // Setup scroll-based animations
    setupScrollAnimations();
    
    // Initialize interactive elements
    initializeInteractiveElements();
});

function addCharacterCounter(textarea) {
    var maxLength = 10000;
    var counter = document.createElement('div');
    counter.className = 'text-muted small mt-1';
    counter.innerHTML = `<i class="fas fa-info-circle me-1"></i><span id="char-count">0</span>/${maxLength} characters`;
    
    textarea.parentNode.appendChild(counter);
    
    var updateCounter = function() {
        var current = textarea.value.length;
        var countSpan = document.getElementById('char-count');
        countSpan.textContent = current;
        
        if (current > maxLength * 0.9) {
            counter.classList.add('text-warning');
            counter.classList.remove('text-muted');
        } else if (current > maxLength * 0.95) {
            counter.classList.add('text-danger');
            counter.classList.remove('text-warning', 'text-muted');
        } else {
            counter.classList.add('text-muted');
            counter.classList.remove('text-warning', 'text-danger');
        }
    };
    
    textarea.addEventListener('input', updateCounter);
    updateCounter(); // Initial count
}

function setupAutoSave(form) {
    var inputs = form.querySelectorAll('input, textarea, select');
    var saveKey = 'content_draft_' + (window.location.pathname.includes('edit') ? 
        window.location.pathname.split('/').pop() : 'new');
    
    // Load saved draft
    var savedDraft = localStorage.getItem(saveKey);
    if (savedDraft && !window.location.pathname.includes('edit')) {
        var draftData = JSON.parse(savedDraft);
        if (confirm('A saved draft was found. Would you like to restore it?')) {
            Object.keys(draftData).forEach(key => {
                var input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = draftData[key];
                }
            });
        }
    }
    
    // Auto-save every 30 seconds
    setInterval(function() {
        var formData = {};
        inputs.forEach(input => {
            if (input.name && input.value) {
                formData[input.name] = input.value;
            }
        });
        localStorage.setItem(saveKey, JSON.stringify(formData));
    }, 30000);
    
    // Clear draft on successful submit
    form.addEventListener('submit', function() {
        localStorage.removeItem(saveKey);
    });
}

function setupAdvancedSearch() {
    var searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function() {
            // Could implement live search here
            console.log('Search query:', searchInput.value);
        }, 300);
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + N: New content
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            window.location.href = '/create';
        }
        
        // Ctrl/Cmd + S: Save form (if on create/edit page)
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            var submitButton = document.querySelector('input[type="submit"], button[type="submit"]');
            if (submitButton) {
                event.preventDefault();
                submitButton.click();
            }
        }
        
        // Escape: Close modals
        if (event.key === 'Escape') {
            var modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                var bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    var alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Enhanced File Upload Functionality
function setupDragDropUpload() {
    var uploadZone = document.querySelector('.file-upload-zone');
    var fileInput = document.getElementById('fileInput');
    var filePreviewArea = document.getElementById('filePreviewArea');
    var fileList = document.getElementById('fileList');
    
    if (!uploadZone || !fileInput) return;
    
    // Drag and drop events
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#007bff';
        uploadZone.style.backgroundColor = '#f8f9fa';
    });
    
    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#dee2e6';
        uploadZone.style.backgroundColor = 'transparent';
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#dee2e6';
        uploadZone.style.backgroundColor = 'transparent';
        
        var files = e.dataTransfer.files;
        handleFileSelection(files);
    });
    
    // Click to upload
    uploadZone.addEventListener('click', (e) => {
        if (e.target && e.target.type !== 'file') {
            fileInput.click();
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelection(e.target.files);
    });
    
    function handleFileSelection(files) {
        if (files.length === 0) return;
        
        // Update file input
        var dt = new DataTransfer();
        Array.from(files).forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
        
        displayFilePreview(files);
        validateFiles(files);
    }
    
    function displayFilePreview(files) {
        fileList.innerHTML = '';
        
        if (files.length > 0) {
            filePreviewArea.style.display = 'block';
            
            Array.from(files).forEach((file, index) => {
                var fileItem = createFilePreviewItem(file, index);
                fileList.appendChild(fileItem);
            });
        } else {
            filePreviewArea.style.display = 'none';
        }
    }
    
    function createFilePreviewItem(file, index) {
        var fileItem = document.createElement('div');
        fileItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        var fileInfo = document.createElement('div');
        fileInfo.className = 'd-flex align-items-center';
        
        var icon = getFileIcon(file.type, file.name);
        var fileName = document.createElement('span');
        fileName.textContent = file.name;
        fileName.className = 'me-2';
        
        var fileSize = document.createElement('small');
        fileSize.textContent = formatFileSize(file.size);
        fileSize.className = 'text-muted';
        
        fileInfo.appendChild(icon);
        fileInfo.appendChild(fileName);
        fileInfo.appendChild(fileSize);
        
        var removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-sm btn-outline-danger';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.onclick = () => removeFile(index);
        
        fileItem.appendChild(fileInfo);
        fileItem.appendChild(removeBtn);
        
        return fileItem;
    }
    
    function removeFile(index) {
        var dt = new DataTransfer();
        var files = Array.from(fileInput.files);
        
        files.forEach((file, i) => {
            if (i !== index) dt.items.add(file);
        });
        
        fileInput.files = dt.files;
        displayFilePreview(fileInput.files);
    }
    
    function getFileIcon(mimeType, fileName) {
        var icon = document.createElement('i');
        icon.className = 'fas fa-lg text-primary me-2';
        
        var extension = fileName.split('.').pop().toLowerCase();
        
        if (mimeType.startsWith('image/')) {
            icon.className += ' fa-image';
        } else if (mimeType.startsWith('video/')) {
            icon.className += ' fa-video';
        } else if (mimeType.startsWith('audio/')) {
            icon.className += ' fa-music';
        } else if (['pdf'].includes(extension)) {
            icon.className += ' fa-file-pdf';
        } else if (['doc', 'docx'].includes(extension)) {
            icon.className += ' fa-file-word';
        } else if (['xls', 'xlsx'].includes(extension)) {
            icon.className += ' fa-file-excel';
        } else if (['ppt', 'pptx'].includes(extension)) {
            icon.className += ' fa-file-powerpoint';
        } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) {
            icon.className += ' fa-file-archive';
        } else if (['txt', 'rtf'].includes(extension)) {
            icon.className += ' fa-file-alt';
        } else {
            icon.className += ' fa-file';
        }
        
        return icon;
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        var k = 1024;
        var sizes = ['B', 'KB', 'MB', 'GB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    function validateFiles(files) {
        var maxSize = 100 * 1024 * 1024; // 100MB
        var allowedTypes = [
            // Images
            'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp', 'image/svg+xml',
            // Documents
            'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'application/rtf', 'application/vnd.oasis.opendocument.text',
            'text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            // Video
            'video/mp4', 'video/webm', 'video/avi', 'video/quicktime', 'video/x-ms-wmv', 'video/x-flv',
            // Audio
            'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac', 'audio/aac', 'audio/mp4',
            // Archives
            'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
            'application/x-tar', 'application/gzip'
        ];
        
        Array.from(files).forEach(file => {
            if (file.size > maxSize) {
                showNotification(`File "${file.name}" is too large. Maximum size is 100MB.`, 'warning');
            }
        });
    }
}

// ===== MICRO-INTERACTIONS AND DELIGHTFUL UI ANIMATIONS =====

function initializeMicroInteractions() {
    // Add icon bounce effect to buttons with icons
    var iconButtons = document.querySelectorAll('.btn i');
    iconButtons.forEach(button => {
        button.parentElement.classList.add('icon-bounce');
    });
    
    // Initialize loading states for forms
    var forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            var submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                var originalText = submitBtn.textContent;
                submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Submitting<span class="loading-dots"></span>';
                submitBtn.disabled = true;
                
                // Re-enable after a reasonable time if not redirected
                setTimeout(() => {
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 5000);
            }
        });
    });
    
    // Add success animation to successful actions
    var successAlerts = document.querySelectorAll('.alert-success');
    successAlerts.forEach(alert => {
        alert.classList.add('success-bounce');
    });
    
    // Add pulse effect to new content
    var newContent = document.querySelectorAll('[data-new="true"]');
    newContent.forEach(element => {
        element.classList.add('pulse-new');
    });
    
    // Enhance search input with micro-interactions
    var searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(input => {
        input.parentElement.classList.add('search-input');
    });
    
    // Add stagger animation to content grids
    var contentGrids = document.querySelectorAll('.row');
    contentGrids.forEach(grid => {
        if (grid.querySelectorAll('.card').length > 1) {
            grid.classList.add('content-grid');
        }
    });
}

function setupScrollAnimations() {
    // Intersection Observer for reveal animations
    var observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    var observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for scroll-based animations
    var animatedElements = document.querySelectorAll('.card, .alert, .btn-primary');
    animatedElements.forEach(el => {
        el.classList.add('reveal-on-scroll');
        observer.observe(el);
    });
    
    // Parallax effect for background elements
    window.addEventListener('scroll', throttle(() => {
        var scrolled = window.pageYOffset;
        var parallaxElements = document.querySelectorAll('[data-parallax]');
        
        parallaxElements.forEach(element => {
            var speed = element.dataset.parallax || 0.5;
            var yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }, 16));
}

function initializeInteractiveElements() {
    // Enhanced button interactions
    var buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        // Add ripple effect on click
        button.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
        
        // Add subtle hover animations
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Enhanced card interactions
    var cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.zIndex = '';
        });
    });
    
    // Interactive badges
    var badges = document.querySelectorAll('.badge');
    badges.forEach(badge => {
        badge.addEventListener('click', function() {
            this.classList.add('success-bounce');
            setTimeout(() => {
                this.classList.remove('success-bounce');
            }, 800);
        });
    });
    
    // Enhanced form interactions
    var formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('form-focus');
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('form-focus');
        });
        
        // Add floating label effect
        control.addEventListener('input', function() {
            if (this.value.length > 0) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
    
    // Progressive enhancement for file uploads
    var fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            var files = this.files;
            if (files.length > 0) {
                showFileUploadFeedback(files);
            }
        });
    });
    
    // Smooth scrolling for anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var href = this.getAttribute('href');
            if (href && href !== '#') {
                var target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add loading states to navigation links
    var navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (this.href && !this.href.includes('#')) {
                this.innerHTML += ' <span class="loading-spinner ms-2"></span>';
            }
        });
    });
}

function createRippleEffect(event, element) {
    var circle = document.createElement('span');
    var diameter = Math.max(element.clientWidth, element.clientHeight);
    var radius = diameter / 2;
    
    var rect = element.getBoundingClientRect();
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - rect.left - radius}px`;
    circle.style.top = `${event.clientY - rect.top - radius}px`;
    circle.classList.add('ripple');
    
    // Add ripple styles
    circle.style.position = 'absolute';
    circle.style.borderRadius = '50%';
    circle.style.background = 'rgba(255, 255, 255, 0.3)';
    circle.style.transform = 'scale(0)';
    circle.style.animation = 'ripple-animation 0.6s linear';
    circle.style.pointerEvents = 'none';
    
    var rippleKeyframes = `
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    
    if (!document.querySelector('#ripple-styles')) {
        var style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = rippleKeyframes;
        document.head.appendChild(style);
    }
    
    var ripple = element.querySelector('.ripple');
    if (ripple) {
        ripple.remove();
    }
    
    element.appendChild(circle);
    
    setTimeout(() => {
        circle.remove();
    }, 600);
}

function showFileUploadFeedback(files) {
    // Create temporary feedback element
    var feedback = document.createElement('div');
    feedback.className = 'alert alert-success fade-in mt-2';
    feedback.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${files.length} file${files.length > 1 ? 's' : ''} selected successfully!
    `;
    
    var fileInput = document.querySelector('input[type="file"]');
    if (fileInput && fileInput.parentElement) {
        fileInput.parentElement.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }
}

function throttle(func, delay) {
    let timeoutId;
    let lastExecTime = 0;
    return function (...args) {
        var currentTime = Date.now();
        
        if (currentTime - lastExecTime > delay) {
            func.apply(this, args);
            lastExecTime = currentTime;
        } else {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
                lastExecTime = Date.now();
            }, delay - (currentTime - lastExecTime));
        }
    };
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 4000) {
    var notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.3s ease-out;
    `;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getIconForType(type)} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, duration);
    
    return notification;
}

function getIconForType(type) {
    var icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle',
        'primary': 'star'
    };
    return icons[type] || 'info-circle';
}

// Enhanced loading states
function showLoadingState(element, text = 'Loading') {
    if (element) {
        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = `
            <span class="loading-spinner me-2"></span>
            ${text}<span class="loading-dots"></span>
        `;
        element.disabled = true;
    }
}

function hideLoadingState(element) {
    if (element && element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        element.disabled = false;
        delete element.dataset.originalContent;
    }
}

// Page transition effects
function initializePageTransitions() {
    // Fade in content on page load
    document.body.style.opacity = '0';
    window.addEventListener('load', () => {
        document.body.style.transition = 'opacity 0.3s ease-in';
        document.body.style.opacity = '1';
    });
    
    // Smooth page transitions for navigation
    var pageLinks = document.querySelectorAll('a:not([href^="#"]):not([href^="mailto"]):not([href^="tel"])');
    pageLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.hostname === window.location.hostname) {
                e.preventDefault();
                document.body.style.transition = 'opacity 0.2s ease-out';
                document.body.style.opacity = '0';
                
                setTimeout(() => {
                    window.location.href = this.href;
                }, 200);
            }
        });
    });
}

// Initialize page transitions
initializePageTransitions();

// Shopping Cart Shortcuts and Quick Actions
function setupCartShortcuts() {
    // Cart count update functionality
    updateCartCount();
    
    // Quick add to cart with keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Shift + C for cart
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
            e.preventDefault();
            window.location.href = '/cart';
        }
        
        // Ctrl/Cmd + Shift + S for shop
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            window.location.href = '/shop';
        }
    });
    
    // Quick add to cart buttons enhancement
    var addToCartButtons = document.querySelectorAll('form[action*="add_to_cart"]');
    addToCartButtons.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            quickAddToCart(form);
        });
    });
    
    // Cart item quick actions
    setupCartItemActions();
    
    // Mini cart preview on hover
    setupMiniCartPreview();
}

function updateCartCount() {
    fetch('/api/cart/count')
        .then(response => response.json())
        .then(data => {
            var cartBadge = document.getElementById('cart-count');
            if (cartBadge) {
                cartBadge.textContent = data.count || 0;
                cartBadge.style.display = data.count > 0 ? 'inline' : 'none';
            }
        })
        .catch(error => {
            console.log('Cart count update temporarily unavailable');
        });
}

function quickAddToCart(form) {
    var formData = new FormData(form);
    var submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        showLoadingState(submitBtn, 'Adding');
    }
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Item added to cart!', 'success', 2000);
            updateCartCount();
            
            // Add visual feedback
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
                submitBtn.classList.add('btn-success');
                setTimeout(() => {
                    hideLoadingState(submitBtn);
                    submitBtn.classList.remove('btn-success');
                }, 1500);
            }
        } else {
            showNotification(data.message || 'Error adding item', 'danger');
            if (submitBtn) hideLoadingState(submitBtn);
        }
    })
    .catch(error => {
        showNotification('Unable to add item to cart', 'warning');
        if (submitBtn) hideLoadingState(submitBtn);
    });
}

function setupCartItemActions() {
    // Quick quantity update
    var quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(input => {
        let updateTimeout;
        input.addEventListener('input', function() {
            clearTimeout(updateTimeout);
            updateTimeout = setTimeout(() => {
                quickUpdateQuantity(this);
            }, 1000);
        });
        
        // Keyboard shortcuts for quantity
        input.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.value = parseInt(this.value || 0) + 1;
                quickUpdateQuantity(this);
            } else if (e.key === 'ArrowDown' && parseInt(this.value) > 1) {
                e.preventDefault();
                this.value = parseInt(this.value) - 1;
                quickUpdateQuantity(this);
            }
        });
    });
    
    // Quick remove buttons
    var removeButtons = document.querySelectorAll('a[href*="remove_from_cart"]');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            quickRemoveItem(this.href);
        });
    });
}

function quickUpdateQuantity(input) {
    var form = input.closest('form');
    if (!form) return;
    
    var formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            // Update total if visible
            var totalElement = document.querySelector('.cart-total');
            if (totalElement && data.new_total) {
                totalElement.textContent = '$' + data.new_total.toFixed(2);
            }
        }
    })
    .catch(error => {
        console.log('Quantity update temporarily unavailable');
    });
}

function quickRemoveItem(removeUrl) {
    if (confirm('Remove this item from cart?')) {
        fetch(removeUrl, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Item removed from cart', 'info');
                updateCartCount();
                // Remove the item row
                var itemRow = document.querySelector(`[data-item-id="${data.item_id}"]`);
                if (itemRow) {
                    itemRow.style.transition = 'opacity 0.3s ease';
                    itemRow.style.opacity = '0';
                    setTimeout(() => itemRow.remove(), 300);
                }
            }
        })
        .catch(error => {
            showNotification('Unable to remove item', 'warning');
        });
    }
}

function setupMiniCartPreview() {
    var cartLink = document.getElementById('cart-shortcut');
    if (!cartLink) return;
    
    let previewTimeout;
    let miniCart = null;
    
    cartLink.addEventListener('mouseenter', function() {
        previewTimeout = setTimeout(() => {
            showMiniCartPreview();
        }, 500);
    });
    
    cartLink.addEventListener('mouseleave', function() {
        clearTimeout(previewTimeout);
        setTimeout(() => {
            if (miniCart && !miniCart.matches(':hover')) {
                hideMiniCartPreview();
            }
        }, 200);
    });
}

function showMiniCartPreview() {
    fetch('/api/cart/preview')
        .then(response => response.json())
        .then(data => {
            createMiniCartPreview(data);
        })
        .catch(error => {
            console.log('Cart preview temporarily unavailable');
        });
}

function createMiniCartPreview(cartData) {
    // Remove existing preview
    var existing = document.querySelector('.mini-cart-preview');
    if (existing) existing.remove();
    
    var preview = document.createElement('div');
    preview.className = 'mini-cart-preview position-absolute bg-white border rounded shadow-lg';
    preview.style.cssText = `
        top: 100%;
        right: 0;
        min-width: 300px;
        max-width: 400px;
        z-index: 1050;
        padding: 1rem;
        margin-top: 0.5rem;
    `;
    
    if (cartData.items && cartData.items.length > 0) {
        preview.innerHTML = `
            <h6 class="mb-3">Cart Items (${cartData.items.length})</h6>
            ${cartData.items.slice(0, 3).map(item => `
                <div class="d-flex align-items-center mb-2">
                    <img src="${item.image_url || '/static/placeholder.png'}" 
                         class="rounded me-2" style="width: 40px; height: 40px; object-fit: cover;">
                    <div class="flex-grow-1">
                        <small class="fw-semibold">${item.name}</small>
                        <div class="text-muted small">$${item.price} x ${item.quantity}</div>
                    </div>
                </div>
            `).join('')}
            ${cartData.items.length > 3 ? `<small class="text-muted">...and ${cartData.items.length - 3} more items</small>` : ''}
            <hr>
            <div class="d-flex justify-content-between align-items-center">
                <strong>Total: $${cartData.total}</strong>
                <a href="/cart" class="btn btn-primary btn-sm">View Cart</a>
            </div>
        `;
    } else {
        preview.innerHTML = `
            <div class="text-center py-3">
                <i class="fas fa-shopping-cart fa-2x text-muted mb-2"></i>
                <p class="text-muted mb-0">Your cart is empty</p>
                <a href="/shop" class="btn btn-outline-primary btn-sm mt-2">Start Shopping</a>
            </div>
        `;
    }
    
    var cartLink = document.getElementById('cart-shortcut');
    if (cartLink) {
        var container = cartLink.closest('.dropdown') || cartLink.parentElement;
        container.style.position = 'relative';
        container.appendChild(preview);
        
        // Add hover behavior to preview
        preview.addEventListener('mouseleave', function() {
            setTimeout(() => hideMiniCartPreview(), 200);
        });
    }
}

function hideMiniCartPreview() {
    var preview = document.querySelector('.mini-cart-preview');
    if (preview) {
        preview.style.transition = 'opacity 0.2s ease';
        preview.style.opacity = '0';
        setTimeout(() => preview.remove(), 200);
    }
}

// Enhanced Dropdown Menu Hover Timing Control
function setupDropdownHoverTiming() {
    const dropdowns = document.querySelectorAll('.navbar .dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!toggle || !menu) return;
        
        let showTimeout;
        let hideTimeout;
        let isMenuOpen = false;
        
        // Show menu with delay on hover
        const showMenu = () => {
            clearTimeout(hideTimeout);
            if (!isMenuOpen) {
                showTimeout = setTimeout(() => {
                    menu.classList.add('show');
                    toggle.classList.add('show');
                    toggle.setAttribute('aria-expanded', 'true');
                    isMenuOpen = true;
                    
                    // Add smooth slide-in animation
                    menu.style.transform = 'translateY(-10px)';
                    menu.style.opacity = '0';
                    setTimeout(() => {
                        menu.style.transition = 'all 0.3s ease';
                        menu.style.transform = 'translateY(0)';
                        menu.style.opacity = '1';
                    }, 10);
                }, 300); // 300ms delay before showing
            }
        };
        
        // Hide menu with longer delay for better UX
        const hideMenu = () => {
            clearTimeout(showTimeout);
            if (isMenuOpen) {
                hideTimeout = setTimeout(() => {
                    menu.style.transition = 'all 0.2s ease';
                    menu.style.transform = 'translateY(-5px)';
                    menu.style.opacity = '0';
                    
                    setTimeout(() => {
                        menu.classList.remove('show');
                        toggle.classList.remove('show');
                        toggle.setAttribute('aria-expanded', 'false');
                        isMenuOpen = false;
                        menu.style.transform = '';
                        menu.style.opacity = '';
                        menu.style.transition = '';
                    }, 200);
                }, 500); // 500ms pause before hiding
            }
        };
        
        // Mouse enter handlers
        dropdown.addEventListener('mouseenter', showMenu);
        
        // Mouse leave handlers with intelligent timing
        dropdown.addEventListener('mouseleave', hideMenu);
        
        // Menu item hover pause - cancel hide when hovering menu items
        menu.addEventListener('mouseenter', () => {
            clearTimeout(hideTimeout);
        });
        
        // Resume hide timing when leaving menu
        menu.addEventListener('mouseleave', hideMenu);
        
        // Enhanced menu item interactions
        const menuItems = menu.querySelectorAll('.dropdown-item');
        menuItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                // Clear any pending hide timeouts when hovering items
                clearTimeout(hideTimeout);
                
                // Add smooth highlight effect
                this.style.transition = 'all 0.15s ease';
                this.style.transform = 'translateX(3px)';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
        
        // Keyboard navigation support
        toggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if (isMenuOpen) {
                    hideMenu();
                } else {
                    showMenu();
                }
            }
            
            if (e.key === 'Escape' && isMenuOpen) {
                hideMenu();
                toggle.focus();
            }
        });
        
        // Arrow key navigation within menu
        menu.addEventListener('keydown', (e) => {
            const items = menu.querySelectorAll('.dropdown-item:not(.disabled)');
            const currentIndex = Array.from(items).indexOf(document.activeElement);
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                const nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
                items[nextIndex].focus();
            }
            
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                const prevIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
                items[prevIndex].focus();
            }
            
            if (e.key === 'Escape') {
                hideMenu();
                toggle.focus();
            }
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && isMenuOpen) {
                hideMenu();
            }
        });
        
        // Touch device support
        if ('ontouchstart' in window) {
            dropdown.addEventListener('touchstart', (e) => {
                if (!isMenuOpen) {
                    e.preventDefault();
                    showMenu();
                }
            });
        }
    });
    
    // Enhanced mobile responsiveness
    const handleResize = () => {
        const isMobile = window.innerWidth < 992;
        dropdowns.forEach(dropdown => {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu && isMobile) {
                // Reset any custom positioning on mobile
                menu.style.transform = '';
                menu.style.opacity = '';
                menu.style.transition = '';
            }
        });
    };
    
    window.addEventListener('resize', throttle(handleResize, 250));
    handleResize(); // Run once on init
}

// Floating Cart (漂浮購物車) Functionality
function setupFloatingCart() {
    var floatingCart = document.getElementById('floatingCart');
    var floatingCartMini = document.getElementById('floatingCartMini');
    var floatingCartBadge = document.getElementById('floatingCartBadge');
    
    if (!floatingCart) return;
    
    // Update floating cart display
    updateFloatingCartDisplay();
    
    // Click to toggle mini cart
    floatingCart.addEventListener('click', function() {
        toggleFloatingCartMini();
    });
    
    // Close mini cart when clicking outside
    document.addEventListener('click', function(e) {
        if (!floatingCart.contains(e.target) && !floatingCartMini.contains(e.target)) {
            hideFloatingCartMini();
        }
    });
    
    // Auto-hide mini cart after 10 seconds of no interaction
    let autoHideTimeout;
    floatingCartMini.addEventListener('mouseenter', function() {
        clearTimeout(autoHideTimeout);
    });
    
    floatingCartMini.addEventListener('mouseleave', function() {
        autoHideTimeout = setTimeout(() => {
            hideFloatingCartMini();
        }, 10000);
    });
}

function updateFloatingCartDisplay() {
    fetch('/api/cart/count')
        .then(response => response.json())
        .then(data => {
            var badge = document.getElementById('floatingCartBadge');
            if (badge) {
                badge.textContent = data.count || 0;
                badge.style.display = data.count > 0 ? 'flex' : 'none';
            }
            loadFloatingCartItems();
        })
        .catch(error => {
            console.log('Cart count update temporarily unavailable');
        });
}

function loadFloatingCartItems() {
    fetch('/api/cart/preview')
        .then(response => response.json())
        .then(data => {
            updateFloatingCartContent(data);
        })
        .catch(error => {
            console.log('Cart preview temporarily unavailable');
        });
}

function updateFloatingCartContent(cartData) {
    var cartBody = document.getElementById('floatingCartBody');
    var cartTotal = document.getElementById('floatingCartTotal');
    
    if (!cartBody || !cartTotal) return;
    
    if (cartData.items && cartData.items.length > 0) {
        // Display cart items
        cartBody.innerHTML = cartData.items.map(item => `
            <div class="floating-cart-item">
                <img src="${item.image_url || '/static/uploads/placeholder.png'}" 
                     class="floating-cart-item-image" 
                     alt="${item.name}">
                <div class="floating-cart-item-info">
                    <div class="floating-cart-item-name">${item.name}</div>
                    <div class="floating-cart-item-price">$${parseFloat(item.price).toFixed(2)} × ${item.quantity}</div>
                </div>
            </div>
        `).join('');
        
        cartTotal.textContent = `$${parseFloat(cartData.total || 0).toFixed(2)}`;
    } else {
        // Empty cart state
        cartBody.innerHTML = `
            <div class="floating-cart-empty">
                <i class="fas fa-shopping-cart"></i>
                <p>Your cart is empty</p>
            </div>
        `;
        cartTotal.textContent = '$0.00';
    }
}

function toggleFloatingCartMini() {
    var miniCart = document.getElementById('floatingCartMini');
    if (miniCart) {
        if (miniCart.classList.contains('show')) {
            hideFloatingCartMini();
        } else {
            showFloatingCartMini();
        }
    }
}

function showFloatingCartMini() {
    var miniCart = document.getElementById('floatingCartMini');
    if (miniCart) {
        miniCart.classList.add('show');
        loadFloatingCartItems(); // Refresh cart contents
    }
}

function hideFloatingCartMini() {
    var miniCart = document.getElementById('floatingCartMini');
    if (miniCart) {
        miniCart.classList.remove('show');
    }
}

function createAddToCartAnimation(startElement) {
    var floatingCart = document.getElementById('floatingCart');
    if (!startElement || !floatingCart) return;
    
    var startRect = startElement.getBoundingClientRect();
    var endRect = floatingCart.getBoundingClientRect();
    
    var animation = document.createElement('div');
    animation.className = 'add-to-cart-animation';
    animation.style.left = startRect.left + (startRect.width / 2) - 15 + 'px';
    animation.style.top = startRect.top + (startRect.height / 2) - 15 + 'px';
    
    document.body.appendChild(animation);
    
    // Animate to floating cart
    var deltaX = endRect.left - startRect.left;
    var deltaY = endRect.top - startRect.top;
    
    animation.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    animation.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(0.5)`;
    animation.style.opacity = '0';
    
    setTimeout(() => {
        animation.remove();
        // Pulse the floating cart
        floatingCart.style.animation = 'pulse-badge 0.6s ease';
        setTimeout(() => {
            floatingCart.style.animation = '';
        }, 600);
    }, 800);
}

// Enhanced quick add to cart with animation
function quickAddToCartWithAnimation(form) {
    var formData = new FormData(form);
    var submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        showLoadingState(submitBtn, 'Adding');
    }
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Item added to cart!', 'success', 2000);
            updateFloatingCartDisplay();
            createAddToCartAnimation(submitBtn);
            
            // Add visual feedback
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
                submitBtn.classList.add('btn-success');
                setTimeout(() => {
                    hideLoadingState(submitBtn);
                    submitBtn.classList.remove('btn-success');
                }, 1500);
            }
        } else {
            showNotification(data.message || 'Error adding item', 'danger');
            if (submitBtn) hideLoadingState(submitBtn);
        }
    })
    .catch(error => {
        showNotification('Unable to add item to cart', 'warning');
        if (submitBtn) hideLoadingState(submitBtn);
    });
}

// Override the original quickAddToCart function
function quickAddToCart(form) {
    quickAddToCartWithAnimation(form);
}

// Price Comparison Tooltips
function setupPriceComparison() {
    // Find all price elements and add comparison functionality
    var priceElements = document.querySelectorAll('.product-price, .price, [data-price]');
    
    priceElements.forEach(priceElement => {
        var price = extractPrice(priceElement);
        if (price > 0) {
            setupPriceTooltip(priceElement, price);
        }
    });
}

function extractPrice(element) {
    // Extract price from various formats
    var text = element.textContent || element.dataset.price || '';
    var match = text.match(/\$?([0-9,]+\.?[0-9]*)/);
    return match ? parseFloat(match[1].replace(',', '')) : 0;
}

function setupPriceTooltip(priceElement, price) {
    // Skip if already has tooltip
    if (priceElement.querySelector('.price-tooltip')) return;
    
    // Wrap price in comparison container
    var wrapper = document.createElement('span');
    wrapper.className = 'price-comparison';
    priceElement.parentNode.insertBefore(wrapper, priceElement);
    wrapper.appendChild(priceElement);
    
    // Create tooltip
    var tooltip = document.createElement('div');
    tooltip.className = 'price-tooltip';
    tooltip.innerHTML = `
        <div class="price-loading">
            Loading price insights...
        </div>
    `;
    wrapper.appendChild(tooltip);
    
    // Load price comparison data on hover
    let dataLoaded = false;
    wrapper.addEventListener('mouseenter', function() {
        if (!dataLoaded) {
            loadPriceComparisonData(price, tooltip);
            dataLoaded = true;
        }
    });
}

function loadPriceComparisonData(currentPrice, tooltip) {
    // Get product category and context
    var productCard = tooltip.closest('.card, .product-card, .content-card');
    var category = getProductCategory(productCard);
    
    fetch('/api/price-comparison', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            price: currentPrice,
            category: category
        })
    })
    .then(response => response.json())
    .then(data => {
        updatePriceTooltip(tooltip, currentPrice, data);
    })
    .catch(error => {
        tooltip.innerHTML = `
            <div class="price-tooltip-header">
                <h6 class="price-tooltip-title">📊 Price Analysis</h6>
            </div>
            <div class="price-insights">
                Price comparison temporarily unavailable
            </div>
        `;
    });
}

function updatePriceTooltip(tooltip, currentPrice, data) {
    var trendClass = data.trend === 'up' ? 'trend-up' : 
                      data.trend === 'down' ? 'trend-down' : 'trend-neutral';
    var trendIcon = data.trend === 'up' ? '↗️' : 
                     data.trend === 'down' ? '↘️' : '➡️';
    
    tooltip.innerHTML = `
        <div class="price-tooltip-header">
            <h6 class="price-tooltip-title">📊 Price Analysis</h6>
            ${getPriceBadge(data.value_rating)}
        </div>
        
        <div class="price-comparison-grid">
            <div class="price-stat">
                <div class="price-stat-label">Category Avg</div>
                <div class="price-stat-value">$${data.category_average.toFixed(2)}</div>
            </div>
            <div class="price-stat">
                <div class="price-stat-label">Market Range</div>
                <div class="price-stat-value">$${data.min_price.toFixed(2)} - $${data.max_price.toFixed(2)}</div>
            </div>
            <div class="price-stat">
                <div class="price-stat-label">Percentile</div>
                <div class="price-stat-value">${data.percentile}th</div>
            </div>
            <div class="price-stat">
                <div class="price-stat-label">Similar Items</div>
                <div class="price-stat-value">${data.similar_count}</div>
            </div>
        </div>
        
        <div class="price-trend ${trendClass}">
            <span class="trend-arrow">${trendIcon}</span>
            <span>${data.trend_text}</span>
        </div>
        
        <div class="price-insights">
            ${data.insights}
        </div>
    `;
}

function getPriceBadge(rating) {
    var badges = {
        'excellent': '<span class="price-badge badge-good-deal">Great Deal</span>',
        'good': '<span class="price-badge badge-good-deal">Good Value</span>',
        'average': '<span class="price-badge badge-average">Fair Price</span>',
        'premium': '<span class="price-badge badge-premium">Premium</span>',
        'high': '<span class="price-badge badge-high">High Price</span>'
    };
    return badges[rating] || '';
}

function getProductCategory(productCard) {
    if (!productCard) return 'general';
    
    // Try to extract category from various sources
    var categoryElement = productCard.querySelector('.category, .product-category, [data-category]');
    if (categoryElement) {
        return categoryElement.textContent.trim().toLowerCase() || categoryElement.dataset.category;
    }
    
    // Check product title for category hints
    var titleElement = productCard.querySelector('.card-title, .product-title, h3, h4, h5');
    if (titleElement) {
        var title = titleElement.textContent.toLowerCase();
        if (title.includes('shirt') || title.includes('blouse')) return 'shirts';
        if (title.includes('pant') || title.includes('chino')) return 'pants';
        if (title.includes('jacket') || title.includes('blazer')) return 'jackets';
        if (title.includes('shoe') || title.includes('loafer')) return 'shoes';
        if (title.includes('dress')) return 'dresses';
        if (title.includes('accessory')) return 'accessories';
    }
    
    return 'general';
}

// Enhanced price display with comparison indicators
function enhancePriceDisplays() {
    var priceElements = document.querySelectorAll('.product-price, .price');
    
    priceElements.forEach(element => {
        // Add visual enhancement to show it's interactive
        element.style.borderBottom = '1px dotted #007bff';
        element.style.cursor = 'help';
        element.title = 'Hover for price comparison';
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupDragDropUpload();
    enhancePriceDisplays();
});

// Responsive interactions
function setupResponsiveInteractions() {
    // Adaptive content display based on screen size
    function handleResponsiveContent() {
        var isMobile = window.innerWidth < 768;
        var cards = document.querySelectorAll('.content-card');
        
        cards.forEach(card => {
            var content = card.querySelector('.card-text');
            if (content && isMobile) {
                // Truncate content on mobile
                var originalText = content.textContent;
                if (originalText.length > 100) {
                    content.textContent = originalText.substring(0, 100) + '...';
                }
            }
        });
    }
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(handleResponsiveContent, 100);
    });
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleResponsiveContent, 250);
    });
    
    handleResponsiveContent();
}

// Mobile-specific optimizations
function setupMobileOptimizations() {
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
        // Prevent zoom on form focus for iOS
        var formInputs = document.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            if (input.style.fontSize === '' || parseFloat(input.style.fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });
        
        // Add mobile-specific classes
        document.body.classList.add('mobile-device');
        
        // Optimize image loading
        var images = document.querySelectorAll('img[data-src]');
        if (images.length > 0) {
            var imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        var img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }
    }
}

// Touch device enhancements
function setupTouchEnhancements() {
    var supportsTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (supportsTouch) {
        document.body.classList.add('touch-device');
        
        // Enhanced touch feedback for buttons
        var touchElements = document.querySelectorAll('.btn, .card, .nav-link');
        touchElements.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            element.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            });
            
            element.addEventListener('touchcancel', function() {
                this.classList.remove('touch-active');
            });
        });
        
        // Swipe gesture support for cards
        let startX, startY, distX, distY;
        var threshold = 100;
        
        var swipeableCards = document.querySelectorAll('.content-card');
        swipeableCards.forEach(card => {
            card.addEventListener('touchstart', function(e) {
                var touch = e.changedTouches[0];
                startX = touch.pageX;
                startY = touch.pageY;
            }, { passive: true });
            
            card.addEventListener('touchend', function(e) {
                var touch = e.changedTouches[0];
                distX = touch.pageX - startX;
                distY = touch.pageY - startY;
                
                if (Math.abs(distX) > threshold && Math.abs(distY) < threshold) {
                    if (distX < 0) {
                        // Swipe left - quick view
                        var viewLink = this.querySelector('a[href*="view_content"]');
                        if (viewLink) {
                            window.location.href = viewLink.href;
                        }
                    }
                }
            }, { passive: true });
        });
    }
}

// Responsive navigation enhancements
function setupResponsiveNavigation() {
    var navbar = document.querySelector('.navbar');
    var navbarToggler = document.querySelector('.navbar-toggler');
    var navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbar.contains(e.target) && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
        
        // Close mobile menu when clicking nav link
        var navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    setTimeout(() => navbarToggler.click(), 100);
                }
            });
        });
    }
}

// Initialize responsive features
document.addEventListener('DOMContentLoaded', function() {
    setupResponsiveNavigation();
});

// AI Relevance Score Functions
function loadAIRelevanceScores() {
    var contentCards = document.querySelectorAll('[data-content-id]');
    if (contentCards.length === 0) return;
    
    var contentIds = Array.from(contentCards).map(card => 
        parseInt(card.getAttribute('data-content-id'))
    ).filter(id => !isNaN(id));
    
    if (contentIds.length === 0) return;
    
    // Batch request for relevance scores
    fetch('/api/content/batch-relevance-scores', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content_ids: contentIds
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.results) {
            displayRelevanceScores(data.results);
        }
    })
    .catch(error => {
        console.log('AI scoring temporarily unavailable');
    });
}

function displayRelevanceScores(scores) {
    Object.entries(scores).forEach(([contentId, analysis]) => {
        var card = document.querySelector(`[data-content-id="${contentId}"]`);
        if (!card || !analysis.overall_score) return;
        
        var score = analysis.overall_score;
        var scoreElement = createScoreBadge(score);
        
        // Find the best position to insert the score badge
        var cardHeader = card.querySelector('.card-header');
        var cardBody = card.querySelector('.card-body');
        var targetElement = cardHeader || cardBody;
        
        if (targetElement) {
            // Remove existing score if present
            var existingScore = card.querySelector('.ai-relevance-score');
            if (existingScore) {
                existingScore.remove();
            }
            
            // Add new score badge
            targetElement.style.position = 'relative';
            targetElement.appendChild(scoreElement);
        }
    });
}

function createScoreBadge(score) {
    var badge = document.createElement('div');
    badge.className = 'ai-relevance-score';
    badge.style.cssText = `
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        z-index: 10;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    `;
    
    // Set color based on score
    let bgColor;
    if (score >= 8) {
        bgColor = 'linear-gradient(135deg, #28a745, #20c997)';
    } else if (score >= 6) {
        bgColor = 'linear-gradient(135deg, #17a2b8, #007bff)';
    } else if (score >= 4) {
        bgColor = 'linear-gradient(135deg, #ffc107, #fd7e14)';
    } else {
        bgColor = 'linear-gradient(135deg, #dc3545, #e83e8c)';
    }
    
    badge.style.background = bgColor;
    badge.textContent = score.toFixed(1);
    
    // Add hover effect
    badge.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
        this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.25)';
    });
    
    badge.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
        this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
    });
    
    // Add tooltip
    badge.title = `AI Relevance Score: ${score.toFixed(1)}/10`;
    
    return badge;
}

function initializeAIScoring() {
    // Load scores on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadAIRelevanceScores);
    } else {
        loadAIRelevanceScores();
    }
    
    // Reload scores when new content is dynamically added
    var observer = new MutationObserver(function(mutations) {
        let shouldReload = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.hasAttribute && node.hasAttribute('data-content-id')) {
                        shouldReload = true;
                    }
                });
            }
        });
        
        if (shouldReload) {
            setTimeout(loadAIRelevanceScores, 500);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Real-time AI Score Updates
function refreshAIScore(contentId) {
    fetch(`/api/content/${contentId}/relevance-score`)
        .then(response => response.json())
        .then(data => {
            if (data.overall_score) {
                var scores = {};
                scores[contentId] = data;
                displayRelevanceScores(scores);
            }
        })
        .catch(error => {
            console.log('Could not refresh AI score');
        });
}

// Enhanced content card interactions with AI features
function enhanceContentCardsWithAI() {
    var contentCards = document.querySelectorAll('.content-card, .card');
    
    contentCards.forEach(card => {
        var contentId = card.getAttribute('data-content-id');
        if (!contentId) return;
        
        // Add AI analysis quick access
        var cardFooter = card.querySelector('.card-footer');
        if (cardFooter) {
            var aiButton = document.createElement('button');
            aiButton.className = 'btn btn-sm btn-outline-info me-2';
            aiButton.innerHTML = '<i class="fas fa-brain me-1"></i>AI';
            aiButton.title = 'View AI Analysis';
            aiButton.onclick = () => {
                window.location.href = `/content/${contentId}/ai-analysis`;
            };
            
            var buttonGroup = cardFooter.querySelector('.btn-group, .d-flex');
            if (buttonGroup) {
                buttonGroup.insertBefore(aiButton, buttonGroup.firstChild);
            }
        }
    });
}

// Initialize AI features
document.addEventListener('DOMContentLoaded', function() {
    initializeAIScoring();
    enhanceContentCardsWithAI();
});

// Skeleton Loading System
function initializeSkeletonLoading() {
    // Set up skeleton loading for forms and AJAX requests
    setupFormSkeletonLoading();
    setupAjaxSkeletonLoading();
    setupImageLoadingSkeletons();
    setupPageNavigationSkeletons();
}

function setupFormSkeletonLoading() {
    // Add skeleton loading to form submissions
    var forms = document.querySelectorAll('form[data-skeleton-target]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            var targetSelector = this.dataset.skeletonTarget;
            var target = document.querySelector(targetSelector);
            
            if (target) {
                showSkeletonLoading(target, this.dataset.skeletonType || 'content');
            }
        });
    });
}

function setupAjaxSkeletonLoading() {
    // Intercept fetch requests and show skeletons
    var originalFetch = window.fetch;
    
    window.fetch = function(url, options = {}) {
        // Check if skeleton loading is requested
        if (options.skeletonTarget) {
            var target = document.querySelector(options.skeletonTarget);
            if (target) {
                showSkeletonLoading(target, options.skeletonType || 'content');
            }
        }
        
        return originalFetch.apply(this, arguments)
            .then(response => {
                // Hide skeleton when response arrives
                if (options.skeletonTarget) {
                    var target = document.querySelector(options.skeletonTarget);
                    if (target) {
                        setTimeout(() => hideSkeletonLoading(target), 100);
                    }
                }
                return response;
            })
            .catch(error => {
                // Hide skeleton on error too
                if (options.skeletonTarget) {
                    var target = document.querySelector(options.skeletonTarget);
                    if (target) {
                        hideSkeletonLoading(target);
                    }
                }
                throw error;
            });
    };
}

function setupImageLoadingSkeletons() {
    // Add skeleton loading for images
    var images = document.querySelectorAll('img[data-skeleton]');
    
    images.forEach(img => {
        if (!img.complete) {
            var skeleton = createImageSkeleton();
            img.parentNode.insertBefore(skeleton, img);
            img.style.display = 'none';
            
            img.onload = function() {
                skeleton.remove();
                this.style.display = '';
            };
            
            img.onerror = function() {
                skeleton.remove();
                this.style.display = '';
            };
        }
    });
}

function setupPageNavigationSkeletons() {
    // Add skeleton loading for page navigation
    var navLinks = document.querySelectorAll('a[data-skeleton-page]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.dataset.skeletonPage === 'true') {
                showPageLoadingSkeleton();
            }
        });
    });
}

function showSkeletonLoading(container, type = 'content') {
    if (!container) return;
    
    // Store original content
    if (!container.dataset.originalContent) {
        container.dataset.originalContent = container.innerHTML;
    }
    
    // Generate skeleton based on type
    var skeletonHTML = generateSkeletonHTML(type);
    
    // Add loading class and replace content
    container.classList.add('skeleton-loading');
    container.innerHTML = skeletonHTML;
}

function hideSkeletonLoading(container) {
    if (!container || !container.dataset.originalContent) return;
    
    // Remove loading class and restore content
    container.classList.remove('skeleton-loading');
    container.innerHTML = container.dataset.originalContent;
    delete container.dataset.originalContent;
}

function generateSkeletonHTML(type) {
    switch (type) {
        case 'product-grid':
            return generateProductGridSkeleton();
        case 'product-card':
            return generateProductCardSkeleton();
        case 'content-list':
            return generateContentListSkeleton();
        case 'content-card':
            return generateContentCardSkeleton();
        case 'form':
            return generateFormSkeleton();
        case 'table':
            return generateTableSkeleton();
        case 'profile':
            return generateProfileSkeleton();
        default:
            return generateContentSkeleton();
    }
}

function generateProductGridSkeleton() {
    var skeletons = [];
    for (let i = 0; i < 8; i++) {
        skeletons.push(`
            <div class="col-lg-3 col-md-4 col-sm-6 mb-4">
                <div class="skeleton-product-card">
                    <div class="skeleton skeleton-product-image"></div>
                    <div class="skeleton-product-body">
                        <div class="skeleton skeleton-badge"></div>
                        <div class="skeleton skeleton-text-lg"></div>
                        <div class="skeleton skeleton-text-sm" style="width: 80%;"></div>
                        <div class="skeleton skeleton-price"></div>
                        <div class="skeleton skeleton-button"></div>
                    </div>
                </div>
            </div>
        `);
    }
    return `<div class="row">${skeletons.join('')}</div>`;
}

function generateProductCardSkeleton() {
    return `
        <div class="skeleton-product-card">
            <div class="skeleton skeleton-product-image"></div>
            <div class="skeleton-product-body">
                <div class="skeleton skeleton-badge"></div>
                <div class="skeleton skeleton-text-lg"></div>
                <div class="skeleton skeleton-text-sm" style="width: 80%;"></div>
                <div class="skeleton skeleton-price"></div>
                <div class="skeleton skeleton-button"></div>
            </div>
        </div>
    `;
}

function generateContentListSkeleton() {
    var skeletons = [];
    for (let i = 0; i < 5; i++) {
        skeletons.push(`
            <div class="skeleton-list-item">
                <div class="skeleton skeleton-avatar"></div>
                <div class="skeleton-list-content">
                    <div class="skeleton skeleton-text-lg" style="width: 70%;"></div>
                    <div class="skeleton skeleton-text" style="width: 90%;"></div>
                    <div class="skeleton-list-meta">
                        <div class="skeleton skeleton-text-sm" style="width: 60px;"></div>
                        <div class="skeleton skeleton-text-sm" style="width: 80px;"></div>
                        <div class="skeleton skeleton-text-sm" style="width: 100px;"></div>
                    </div>
                </div>
            </div>
        `);
    }
    return skeletons.join('');
}

function generateContentCardSkeleton() {
    return `
        <div class="skeleton-content-card">
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text" style="width: 85%;"></div>
            <div class="skeleton skeleton-text" style="width: 60%;"></div>
            <div class="skeleton skeleton-line"></div>
            <div class="d-flex justify-content-between">
                <div class="skeleton skeleton-text-sm" style="width: 120px;"></div>
                <div class="skeleton skeleton-button"></div>
            </div>
        </div>
    `;
}

function generateFormSkeleton() {
    return `
        <div class="skeleton-card">
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-text-lg" style="height: 40px; margin-bottom: 1rem;"></div>
            <div class="skeleton skeleton-text-lg" style="height: 40px; margin-bottom: 1rem;"></div>
            <div class="skeleton skeleton-text-lg" style="height: 100px; margin-bottom: 1rem;"></div>
            <div class="skeleton skeleton-button"></div>
        </div>
    `;
}

function generateTableSkeleton() {
    var rows = [];
    for (let i = 0; i < 6; i++) {
        rows.push(`
            <div class="skeleton-table-row">
                <div class="skeleton skeleton-table-cell skeleton-text"></div>
                <div class="skeleton skeleton-table-cell skeleton-text"></div>
                <div class="skeleton skeleton-table-cell skeleton-text"></div>
                <div class="skeleton skeleton-table-cell skeleton-button"></div>
            </div>
        `);
    }
    return rows.join('');
}

function generateProfileSkeleton() {
    return `
        <div class="skeleton-card">
            <div class="d-flex align-items-center mb-4">
                <div class="skeleton skeleton-avatar-lg me-3"></div>
                <div>
                    <div class="skeleton skeleton-text-lg" style="width: 200px;"></div>
                    <div class="skeleton skeleton-text" style="width: 150px;"></div>
                </div>
            </div>
            <div class="skeleton skeleton-line"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text" style="width: 80%;"></div>
            <div class="skeleton skeleton-text" style="width: 60%;"></div>
        </div>
    `;
}

function generateContentSkeleton() {
    return `
        <div class="skeleton-card">
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text" style="width: 90%;"></div>
            <div class="skeleton skeleton-text" style="width: 75%;"></div>
            <div class="skeleton skeleton-line"></div>
            <div class="skeleton skeleton-button"></div>
        </div>
    `;
}

function createImageSkeleton() {
    var skeleton = document.createElement('div');
    skeleton.className = 'skeleton skeleton-image';
    return skeleton;
}

function showPageLoadingSkeleton() {
    var overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-spinner"></div>
    `;
    document.body.appendChild(overlay);
    
    // Remove after page loads
    window.addEventListener('load', function() {
        overlay.remove();
    });
}

// Utility functions for manual skeleton control
function showProductGridSkeleton(container) {
    showSkeletonLoading(container, 'product-grid');
}

function showContentListSkeleton(container) {
    showSkeletonLoading(container, 'content-list');
}

function showFormSkeleton(container) {
    showSkeletonLoading(container, 'form');
}

// Enhanced AJAX with skeleton loading
function fetchWithSkeleton(url, options = {}) {
    var { skeletonTarget, skeletonType, ...fetchOptions } = options;
    
    if (skeletonTarget) {
        var target = document.querySelector(skeletonTarget);
        if (target) {
            showSkeletonLoading(target, skeletonType || 'content');
        }
    }
    
    return fetch(url, fetchOptions)
        .then(response => {
            if (skeletonTarget) {
                var target = document.querySelector(skeletonTarget);
                if (target) {
                    setTimeout(() => hideSkeletonLoading(target), 100);
                }
            }
            return response;
        })
        .catch(error => {
            if (skeletonTarget) {
                var target = document.querySelector(skeletonTarget);
                if (target) {
                    hideSkeletonLoading(target);
                }
            }
            throw error;
        });
}

// Enhanced Fashion Experience Interactions
function initFashionExperience() {
    // Sophisticated Product Card Animations
    document.querySelectorAll('.product-card, .recommendation-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
        
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.02)';
            this.style.boxShadow = '0 25px 50px rgba(0,0,0,0.2)';
            this.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            
            // Enhance image on hover
            var image = this.querySelector('.product-image');
            if (image) {
                image.style.transform = 'scale(1.1)';
                image.style.filter = 'brightness(1.1) saturate(1.2)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 4px 20px rgba(0,0,0,0.08)';
            
            var image = this.querySelector('.product-image');
            if (image) {
                image.style.transform = 'scale(1)';
                image.style.filter = 'brightness(1) saturate(1)';
            }
        });
    });

    // Premium Button Interactions
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 12px 24px rgba(0,0,0,0.15)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'initial';
        });
        
        button.addEventListener('click', function(e) {
            // Create ripple effect
            var ripple = document.createElement('span');
            var rect = this.getBoundingClientRect();
            var size = Math.max(rect.width, rect.height);
            var x = e.clientX - rect.left - size / 2;
            var y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255,255,255,0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Enhanced Badge Animations
    document.querySelectorAll('.badge, .badge-enhanced').forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
            this.style.boxShadow = '0 8px 16px rgba(0,0,0,0.2)';
        });
        
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = 'initial';
        });
    });

    // Price Animation Effects
    document.querySelectorAll('.price-enhanced, .product-price').forEach(price => {
        price.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.08)';
            this.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
        
        price.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Parallax Scroll Effect for Hero Elements
    window.addEventListener('scroll', function() {
        var scrolled = window.pageYOffset;
        var parallaxElements = document.querySelectorAll('.hero-banner, .floating-cards');
        
        parallaxElements.forEach(element => {
            var speed = 0.5;
            var yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    });

    // Staggered Animation for Product Grids
    var observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    var observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.product-card, .recommendation-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// CSS Keyframes for ripple effect
if (!document.querySelector('#fashion-styles')) {
    var style = document.createElement('style');
    style.id = 'fashion-styles';
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize fashion experience on DOM load
document.addEventListener('DOMContentLoaded', initFashionExperience);

// Responsive Swipe Gestures for Mobile Interactions








// Helper functions for swipe gestures






// ================================
// Floating Action Button with Micro-Interactions
// ================================

function initFloatingActionButton() {
    const fab = document.querySelector('.fab');
    const fabMenu = document.querySelector('.fab-menu');
    
    if (!fab || !fabMenu) return;
    
    let isMenuOpen = false;
    let lastScrollY = window.scrollY;
    
    // Toggle menu
    fab.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleFabMenu();
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (isMenuOpen && !fabMenu.contains(e.target)) {
            closeFabMenu();
        }
    });
    
    // Keyboard support
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isMenuOpen) {
            closeFabMenu();
        }
    });
    
    // Scroll behavior
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > lastScrollY && currentScrollY > 100) {
            fab.style.transform = 'translateY(100px)';
        } else {
            fab.style.transform = 'translateY(0)';
        }
        
        lastScrollY = currentScrollY;
    });
    
    function toggleFabMenu() {
        if (isMenuOpen) {
            closeFabMenu();
        } else {
            openFabMenu();
        }
    }
    
    function openFabMenu() {
        isMenuOpen = true;
        fab.classList.add('active');
        fabMenu.classList.add('active');
        
        // Stagger animation for menu items
        const menuItems = fabMenu.querySelectorAll('.fab-menu-item');
        menuItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.transform = 'translateY(0) scale(1)';
                item.style.opacity = '1';
            }, index * 50);
        });
    }
    
    function closeFabMenu() {
        isMenuOpen = false;
        fab.classList.remove('active');
        fabMenu.classList.remove('active');
        
        const menuItems = fabMenu.querySelectorAll('.fab-menu-item');
        menuItems.forEach(item => {
            item.style.transform = 'translateY(20px) scale(0.8)';
            item.style.opacity = '0';
        });
    }
}

function shareContent(contentId) {
    if (navigator.share) {
        navigator.share({
            title: 'Check out this content',
            url: window.location.origin + '/view_content/' + contentId
        });
    } else {
        // Fallback to clipboard
        var url = window.location.origin + '/view_content/' + contentId;
        navigator.clipboard.writeText(url).then(function() {
            showToast('Link copied to clipboard');
        });
    }
}

function bookmarkContent(contentId) {
    // Add to local storage bookmarks
    var bookmarks = JSON.parse(localStorage.getItem('bookmarked_content') || '[]');
    if (!bookmarks.includes(contentId)) {
        bookmarks.push(contentId);
        localStorage.setItem('bookmarked_content', JSON.stringify(bookmarks));
    }
}








function showToast(message) {
    // Create or use existing toast container
    var toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    var toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = '<div class="toast-body">' + message + '</div>';
    
    toastContainer.appendChild(toast);
    
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Clean up after toast is hidden
    toast.addEventListener('hidden.bs.toast', function() {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
}

// Export functions for use in other scripts
window.ContentManager = {
    showNotification,
    formatDateTime,
    truncateText,
    setupDragDropUpload,
    setupResponsiveInteractions,
    setupMobileOptimizations,
    setupTouchEnhancements,
    loadAIRelevanceScores,
    refreshAIScore,
    initializeAIScoring,
    showSkeletonLoading,
    hideSkeletonLoading,
    fetchWithSkeleton,
    showProductGridSkeleton,
    showContentListSkeleton,
    showFormSkeleton,
    initFashionExperience,
    initFloatingActionButton,
    initSocialMediaSharing
};

// ================================
// Social Media Sharing with Dynamic Preview
// ================================

function initSocialMediaSharing() {
    const shareButtons = document.querySelectorAll('.social-share-btn');
    let currentShareData = null;
    
    shareButtons.forEach(button => {
        button.addEventListener('click', handleSocialShare);
    });
    
    // Handle share confirmation
    const confirmBtn = document.getElementById('confirmShareBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', executeShare);
    }
}

function handleSocialShare(event) {
    const button = event.currentTarget;
    const platform = button.dataset.platform;
    const shareData = {
        platform: platform,
        url: button.dataset.url,
        title: button.dataset.title,
        description: button.dataset.description,
        image: button.dataset.image
    };
    
    // Add ripple effect
    createRippleEffect(event, button);
    
    if (platform === 'copy') {
        copyToClipboard(shareData.url, button);
        return;
    }
    
    // Show preview modal for other platforms
    showSharePreview(shareData);
}

function showSharePreview(shareData) {
    currentShareData = shareData;
    const modal = document.getElementById('sharePreviewModal');
    const previewContent = document.getElementById('sharePreviewContent');
    
    if (!modal || !previewContent) return;
    
    // Generate preview based on platform
    const previewHTML = generateSharePreview(shareData);
    previewContent.innerHTML = previewHTML;
    
    // Update modal title
    const modalTitle = document.getElementById('sharePreviewModalLabel');
    if (modalTitle) {
        modalTitle.innerHTML = `
            <i class="fas fa-eye me-2"></i>
            ${getPlatformName(shareData.platform)} Preview
        `;
    }
    
    // Update confirm button
    const confirmBtn = document.getElementById('confirmShareBtn');
    if (confirmBtn) {
        confirmBtn.innerHTML = `
            <i class="${getPlatformIcon(shareData.platform)} me-2"></i>
            Share on ${getPlatformName(shareData.platform)}
        `;
    }
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function generateSharePreview(shareData) {
    const { platform, url, title, description, image } = shareData;
    
    // Extract domain from URL
    let domain = 'discover-amazin.com';
    try {
        domain = new URL(url).hostname;
    } catch (e) {
        // Fallback for relative URLs
        domain = window.location.hostname;
    }
    
    return `
        <div class="share-preview-card share-preview-${platform}">
            ${image ? `<img src="${image}" alt="${title}" class="share-preview-image">` : ''}
            <div class="share-preview-content">
                <div class="share-preview-title">${title}</div>
                <div class="share-preview-description">${description}</div>
                <div class="share-preview-url">${domain}</div>
                ${platform === 'facebook' && title.includes('₩') ? 
                    `<div class="share-preview-price">${title.match(/₩[\d,]+/)?.[0] || ''}</div>` : ''}
            </div>
        </div>
        <div class="mt-3">
            <small class="text-muted">
                <i class="fas fa-info-circle me-1"></i>
                This is how your post will appear on ${getPlatformName(platform)}
            </small>
        </div>
    `;
}

function executeShare() {
    if (!currentShareData) return;
    
    const { platform, url, title, description } = currentShareData;
    let shareUrl = '';
    
    switch (platform) {
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
            break;
        case 'twitter':
            const twitterText = `${title}\n\n${description}`;
            shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(twitterText)}`;
            break;
        case 'whatsapp':
            const whatsappText = `${title}\n\n${description}\n\n${url}`;
            shareUrl = `https://wa.me/?text=${encodeURIComponent(whatsappText)}`;
            break;
    }
    
    if (shareUrl) {
        // Open in new window
        window.open(shareUrl, '_blank', 'width=600,height=400,scrollbars=yes,resizable=yes');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('sharePreviewModal'));
        if (modal) {
            modal.hide();
        }
        
        // Show success feedback
        showShareSuccessFeedback();
    }
}

function copyToClipboard(text, button) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showCopyFeedback(button);
            addSuccessAnimation(button);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            fallbackCopyToClipboard(text, button);
        });
    } else {
        fallbackCopyToClipboard(text, button);
    }
}

function fallbackCopyToClipboard(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback(button);
        addSuccessAnimation(button);
    } catch (err) {
        console.error('Fallback copy failed: ', err);
    }
    
    document.body.removeChild(textArea);
}

function addSuccessAnimation(button) {
    button.classList.add('share-success-animation');
    setTimeout(() => {
        button.classList.remove('share-success-animation');
    }, 600);
}

function showCopyFeedback(button) {
    // Create feedback element
    const feedback = document.createElement('div');
    feedback.className = 'copy-feedback';
    feedback.textContent = 'Link copied!';
    
    // Position relative to button
    button.style.position = 'relative';
    button.appendChild(feedback);
    
    // Show feedback
    setTimeout(() => {
        feedback.classList.add('show');
    }, 100);
    
    // Hide feedback after 2 seconds
    setTimeout(() => {
        feedback.classList.remove('show');
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.parentNode.removeChild(feedback);
            }
        }, 300);
    }, 2000);
}

function showShareSuccessFeedback() {
    showSocialToast('Successfully shared! 🎉');
}

function getPlatformName(platform) {
    const names = {
        facebook: 'Facebook',
        twitter: 'Twitter',
        whatsapp: 'WhatsApp',
        copy: 'Copy Link'
    };
    return names[platform] || platform;
}

function getPlatformIcon(platform) {
    const icons = {
        facebook: 'fab fa-facebook-f',
        twitter: 'fab fa-twitter',
        whatsapp: 'fab fa-whatsapp',
        copy: 'fas fa-link'
    };
    return icons[platform] || 'fas fa-share';
}

// Enhanced toast notification for social sharing
function showSocialToast(message, type = 'success', duration = 3000) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            ${message}
        </div>
    `;
    
    // Add toast styles
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : '#17a2b8'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        transform: translateX(100%);
        transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        font-weight: 500;
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Animate out
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
}

// Swipe gesture system removed per user request

// SwipeManager class removed

// Product Card Swipe Functionality removed





// Navigation Swipe Functionality




// Modal Swipe Functionality



// Image Gallery Swipe Functionality



// General Page Swipe Functionality



// Feedback Functions



// Utility Functions
function updateCartCount() {
    fetch('/api/cart_count')
        .then(response => response.json())
        .then(data => {
            const cartCounts = document.querySelectorAll('#cart-count, .cart-count');
            cartCounts.forEach(count => {
                count.textContent = data.count;
            });
        })
        .catch(error => console.error('Error updating cart count:', error));
}

function updateWishlistCount() {
    // Update wishlist indicators in the UI
    const wishlistCounts = document.querySelectorAll('.wishlist-count');
    fetch('/api/wishlist_count')
        .then(response => response.json())
        .then(data => {
            wishlistCounts.forEach(count => {
                count.textContent = data.count;
            });
        })
        .catch(error => console.error('Error updating wishlist count:', error));
}
