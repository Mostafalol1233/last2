
// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        const htmlElement = document.documentElement;
        const moonIcon = '<i class="fas fa-moon"></i>';
        const sunIcon = '<i class="fas fa-sun"></i>';
        
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-bs-theme', newTheme);
            themeToggle.innerHTML = newTheme === 'dark' ? moonIcon : sunIcon;
        });
    }
    
    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Handle video deletion confirmation
    const deleteVideoButtons = document.querySelectorAll('.delete-video-btn');
    if (deleteVideoButtons.length > 0) {
        deleteVideoButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا الإجراء.')) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Handle post deletion confirmation
    const deletePostButtons = document.querySelectorAll('.delete-post-btn');
    if (deletePostButtons.length > 0) {
        deletePostButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('هل أنت متأكد من حذف هذا المنشور؟ لا يمكن التراجع عن هذا الإجراء.')) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Auto-resize textarea
    const textareas = document.querySelectorAll('textarea');
    if (textareas.length > 0) {
        textareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        });
    }
    
    // Video URL validator
    const videoUrlInput = document.getElementById('url');
    if (videoUrlInput) {
        videoUrlInput.addEventListener('blur', function() {
            const url = this.value.trim();
            if (url && !(
                url.includes('youtube.com/watch') || 
                url.includes('youtu.be/') || 
                url.includes('vimeo.com/') ||
                url.includes('dailymotion.com/video/')
            )) {
                alert('الرجاء إدخال رابط فيديو صالح من YouTube أو Vimeo أو Dailymotion');
            }
        });
    }
});
