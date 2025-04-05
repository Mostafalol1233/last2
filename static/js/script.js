// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        const htmlElement = document.documentElement;
        const moonIcon = '<i class="fas fa-moon"></i>';
        const sunIcon = '<i class="fas fa-sun"></i>';
        
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            htmlElement.setAttribute('data-bs-theme', savedTheme);
            themeToggle.innerHTML = savedTheme === 'dark' ? sunIcon : moonIcon;
        }
        
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeToggle.innerHTML = newTheme === 'dark' ? sunIcon : moonIcon;
        });
    }
    
    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Handle deletion confirmations with improved UI
    const setupDeleteConfirmation = (selector, message) => {
        const buttons = document.querySelectorAll(selector);
        if (buttons.length > 0) {
            buttons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Create modal programmatically
                    const modalId = 'confirmDeleteModal';
                    let modal = document.getElementById(modalId);
                    
                    if (!modal) {
                        const modalHTML = `
                            <div class="modal fade" id="${modalId}" tabindex="-1" aria-hidden="true">
                                <div class="modal-dialog modal-dialog-centered">
                                    <div class="modal-content">
                                        <div class="modal-header">
                                            <h5 class="modal-title">تأكيد الحذف</h5>
                                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                        </div>
                                        <div class="modal-body">
                                            <p>${message}</p>
                                        </div>
                                        <div class="modal-footer">
                                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                                            <button type="button" class="btn btn-danger confirm-delete">تأكيد الحذف</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        document.body.insertAdjacentHTML('beforeend', modalHTML);
                        modal = document.getElementById(modalId);
                    }
                    
                    // Store the original action URL
                    const url = this.getAttribute('href');
                    
                    // Show the modal
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                    
                    // Handle the confirm button
                    const confirmBtn = modal.querySelector('.confirm-delete');
                    
                    // Remove previous event listeners
                    const newConfirmBtn = confirmBtn.cloneNode(true);
                    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
                    
                    newConfirmBtn.addEventListener('click', function() {
                        window.location.href = url;
                    });
                });
            });
        }
    };
    
    // Set up confirmation dialogs
    setupDeleteConfirmation('.delete-video-btn', 'هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا الإجراء.');
    setupDeleteConfirmation('.delete-post-btn', 'هل أنت متأكد من حذف هذا المنشور؟ لا يمكن التراجع عن هذا الإجراء.');
    setupDeleteConfirmation('.delete-note-btn', 'هل أنت متأكد من حذف هذه الملاحظة؟ لا يمكن التراجع عن هذا الإجراء.');
    
    // Auto-resize textarea with improved handling
    const textareas = document.querySelectorAll('textarea');
    if (textareas.length > 0) {
        textareas.forEach(textarea => {
            // Set initial height
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
            
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
            
            // Focus animation
            textarea.addEventListener('focus', function() {
                this.classList.add('focused');
            });
            
            textarea.addEventListener('blur', function() {
                this.classList.remove('focused');
            });
        });
    }
    
    // Video URL validator with improved feedback
    const videoUrlInput = document.getElementById('url');
    if (videoUrlInput) {
        let feedbackElement = document.getElementById('url-feedback');
        
        if (!feedbackElement) {
            feedbackElement = document.createElement('div');
            feedbackElement.id = 'url-feedback';
            feedbackElement.className = 'invalid-feedback';
            videoUrlInput.parentNode.appendChild(feedbackElement);
        }
        
        videoUrlInput.addEventListener('input', function() {
            const url = this.value.trim();
            if (url) {
                const isValid = 
                    url.includes('youtube.com/watch') || 
                    url.includes('youtu.be/') || 
                    url.includes('vimeo.com/') ||
                    url.includes('dailymotion.com/video/');
                
                if (isValid) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    feedbackElement.style.display = 'none';
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                    feedbackElement.textContent = 'الرجاء إدخال رابط فيديو صالح من YouTube أو Vimeo أو Dailymotion';
                    feedbackElement.style.display = 'block';
                }
            } else {
                this.classList.remove('is-valid');
                this.classList.remove('is-invalid');
                feedbackElement.style.display = 'none';
            }
        });
    }
    
    // Enhance forms with visual feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            this.classList.add('was-validated');
        });
    });
    
    // Show loading indicator on form submit
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>جاري المعالجة...';
                this.disabled = true;
                
                // Re-enable after timeout in case of network issues
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 10000);
            }
        });
    });
    
    // Add button effects
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.98)';
        });
        button.addEventListener('mouseup', function() {
            this.style.transform = '';
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Lazy load images
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if ('loading' in HTMLImageElement.prototype) {
        // Browser supports native lazy loading
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback for browsers that don't support lazy loading
        const lazyImageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const lazyImage = entry.target;
                    lazyImage.src = lazyImage.dataset.src;
                    lazyImageObserver.unobserve(lazyImage);
                }
            });
        });
        
        lazyImages.forEach(img => {
            lazyImageObserver.observe(img);
        });
    }
});
