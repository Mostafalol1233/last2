/**
 * Advanced animations and effects
 * 
 * This script enhances the user experience with smooth animations,
 * transitions, and interactive elements.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Preloader animation
    const preloader = document.createElement('div');
    preloader.className = 'preloader';
    preloader.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(preloader);
    
    // Hide preloader after page loads
    window.addEventListener('load', function() {
        preloader.classList.add('fade-out');
        setTimeout(function() {
            preloader.style.display = 'none';
        }, 500);
    });
    
    // Add 'loaded' class to body for entrance animations
    setTimeout(function() {
        document.body.classList.add('loaded');
    }, 300);
    
    // Add badge-new class to new items
    const currentDate = new Date();
    const newItemThreshold = 3; // days
    
    document.querySelectorAll('[data-created]').forEach(item => {
        const createdDate = new Date(item.getAttribute('data-created'));
        const daysDifference = Math.floor((currentDate - createdDate) / (1000 * 60 * 60 * 24));
        
        if (daysDifference <= newItemThreshold) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-danger badge-new ms-2';
            badge.textContent = 'جديد';
            item.querySelector('.card-title, h5, h4, h3').appendChild(badge);
        }
    });
    
    // Button click effects
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size/2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size/2) + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Enhance form inputs
    document.querySelectorAll('.form-control, .form-select').forEach(input => {
        const formGroup = input.closest('.form-group');
        if (formGroup && !formGroup.classList.contains('form-floating')) {
            formGroup.classList.add('form-input-animated');
            
            input.addEventListener('focus', () => {
                formGroup.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                if (!input.value) {
                    formGroup.classList.remove('focused');
                }
            });
            
            // Initialize with correct state
            if (input.value) {
                formGroup.classList.add('focused');
            }
        }
    });
    
    // Enhance card interactions
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover');
        });
    });
    
    // Smooth scroll for anchors
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
    
    // Add custom ripple effect styles
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: rippleEffect 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes rippleEffect {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .form-input-animated label {
            position: absolute;
            top: 0;
            left: 15px;
            height: 100%;
            padding: 1rem 0.75rem;
            pointer-events: none;
            border: 1px solid transparent;
            transform-origin: 0 0;
            transition: opacity .1s ease-in-out,transform .1s ease-in-out;
            color: #6c757d;
        }
        
        .form-input-animated.focused label {
            opacity: .65;
            transform: scale(.85) translateY(-0.5rem) translateX(0.15rem);
        }
    `;
    document.head.appendChild(style);
});