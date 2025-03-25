// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle video deletion confirmation
    const deleteVideoButtons = document.querySelectorAll('.delete-video-btn');
    if (deleteVideoButtons) {
        deleteVideoButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Handle post deletion confirmation
    const deletePostButtons = document.querySelectorAll('.delete-post-btn');
    if (deletePostButtons) {
        deletePostButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Auto-resize textarea
    const textareas = document.querySelectorAll('textarea');
    if (textareas) {
        textareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        });
    }
    
    // Video URL validator (basic check)
    const videoUrlInput = document.getElementById('url');
    if (videoUrlInput) {
        videoUrlInput.addEventListener('blur', function() {
            const url = this.value.trim();
            
            // Basic validation for common video services
            if (url && !(
                url.includes('youtube.com/watch') || 
                url.includes('youtu.be/') || 
                url.includes('vimeo.com/') ||
                url.includes('dailymotion.com/video/')
            )) {
                alert('Please enter a valid video URL from YouTube, Vimeo, or Dailymotion');
            }
        });
    }
});
