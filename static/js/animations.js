/**
 * Enhanced animations and effects
 * 
 * This script adds smooth animations to improve user experience
 * with eye-friendly transitions and effects.
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
    
    // Enhance card animations
    document.querySelectorAll('.card.card-hover').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
        });
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
        
        // Add focus animations
        input.addEventListener('focus', function() {
            this.style.borderLeft = '4px solid var(--primary-color)';
            this.style.transform = 'translateX(5px)';
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.style.borderLeft = '4px solid transparent';
                this.style.transform = 'translateX(0)';
            }
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
    
    // Add scroll animations for elements
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.card, .dashboard-stats');
        
        elements.forEach(element => {
            // Check if element is visible
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('animated');
            }
        });
    };
    
    // Add animation class on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Run once on page load
    animateOnScroll();
    
    // Theme toggle functionality if exists
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const html = document.querySelector('html');
            if (html.getAttribute('data-bs-theme') === 'dark') {
                html.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('theme', 'light');
                this.innerHTML = '<i class="fas fa-moon"></i>';
            } else {
                html.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                this.innerHTML = '<i class="fas fa-sun"></i>';
            }
        });
        
        // Set initial theme based on user preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.querySelector('html').setAttribute('data-bs-theme', savedTheme);
            themeToggle.innerHTML = savedTheme === 'dark' ? 
                '<i class="fas fa-sun"></i>' : 
                '<i class="fas fa-moon"></i>';
        }
    }
    
    // Add custom styles
    const style = document.createElement('style');
    style.textContent = `
        /* Animation classes */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animated {
            animation: fadeInUp 0.6s ease-out forwards;
        }
        
        /* Active label styling */
        label.active {
            transform: translateY(-20px);
            font-size: 0.85em;
            color: var(--primary-color);
        }
        
        /* List group hover effects */
        .list-group-item {
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
        }
        
        .list-group-item:hover {
            background-color: rgba(0,0,0,0.05);
            border-left: 4px solid var(--primary-color);
            transform: translateX(5px);
        }
    `;
    document.head.appendChild(style);
});
