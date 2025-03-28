/**
 * Subtle animations and effects
 * 
 * This script adds minimal animations to improve user experience
 * without being distracting or flashy.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add badge-new class to new items
    const currentDate = new Date();
    const newItemThreshold = 3; // days
    
    document.querySelectorAll('[data-created]').forEach(item => {
        const createdDate = new Date(item.getAttribute('data-created'));
        const daysDifference = Math.floor((currentDate - createdDate) / (1000 * 60 * 60 * 24));
        
        if (daysDifference <= newItemThreshold) {
            const titleEl = item.querySelector('.card-title, h5, h4, h3');
            if (titleEl) {
                const badge = document.createElement('span');
                badge.className = 'badge bg-secondary badge-new ms-2';
                badge.textContent = 'جديد';
                titleEl.appendChild(badge);
            }
        }
    });
    
    // Simple button hover effect (no ripple)
    document.querySelectorAll('.btn-primary').forEach(button => {
        // Replace bright colors with more subtle ones
        button.classList.remove('btn-primary');
        button.classList.add('btn-outline-primary');
    });
    
    document.querySelectorAll('.btn-danger').forEach(button => {
        button.classList.remove('btn-danger');
        button.classList.add('btn-outline-danger');
    });
    
    document.querySelectorAll('.btn-success').forEach(button => {
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-success');
    });
    
    // Improve initialization of form inputs
    document.querySelectorAll('.form-control, .form-select').forEach(input => {
        // Initialize with correct state for filled inputs
        if (input.value) {
            const label = input.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                label.classList.add('active');
            }
        }
    });
    
    // Simple card hover effect
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            this.style.transition = 'box-shadow 0.2s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });
    
    // Smooth scroll for anchors - keep this useful feature
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add subtle styles without overwhelming animations
    const style = document.createElement('style');
    style.textContent = `
        /* Use more subdued colors for interactive elements */
        .btn-outline-primary {
            color: #3d6bb3;
            border-color: #3d6bb3;
        }
        .btn-outline-primary:hover {
            background-color: #3d6bb3;
            color: white;
        }
        
        .btn-outline-danger {
            color: #b45252;
            border-color: #b45252;
        }
        .btn-outline-danger:hover {
            background-color: #b45252;
            color: white;
        }
        
        .btn-outline-success {
            color: #4e8d7c;
            border-color: #4e8d7c;
        }
        .btn-outline-success:hover {
            background-color: #4e8d7c;
            color: white;
        }
        
        /* Subtle transition for all buttons */
        .btn {
            transition: all 0.2s ease;
        }
        
        /* Add active label styling */
        label.active {
            transform: translateY(-20px);
            font-size: 0.85em;
            color: #6c757d;
        }
    `;
    document.head.appendChild(style);
});