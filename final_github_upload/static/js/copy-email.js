/**
 * Email copy functionality
 * 
 * This script adds the ability to click on email addresses
 * and copy them to clipboard with a visual confirmation.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all elements with email copy functionality
    const emailElements = document.querySelectorAll('.email-copy');
    
    emailElements.forEach(element => {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the email from data attribute or from element text
            const email = this.getAttribute('data-email') || this.textContent.trim();
            
            // Copy to clipboard
            navigator.clipboard.writeText(email).then(() => {
                // Create and show tooltip
                const tooltip = document.createElement('div');
                tooltip.className = 'email-copy-tooltip';
                tooltip.textContent = 'تم نسخ البريد الإلكتروني!';
                
                // Position the tooltip near the clicked element
                const rect = this.getBoundingClientRect();
                tooltip.style.top = (rect.top - 40) + 'px';
                tooltip.style.left = (rect.left + rect.width/2 - 75) + 'px';
                
                // Add to body
                document.body.appendChild(tooltip);
                
                // Add visible class for animation
                setTimeout(() => {
                    tooltip.classList.add('visible');
                }, 10);
                
                // Remove tooltip after animation
                setTimeout(() => {
                    tooltip.classList.remove('visible');
                    setTimeout(() => {
                        document.body.removeChild(tooltip);
                    }, 300);
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy email: ', err);
            });
        });
    });
    
    // Add styles for tooltip
    const style = document.createElement('style');
    style.textContent = `
        .email-copy {
            cursor: pointer;
            position: relative;
            transition: all 0.3s ease;
            color: #4e6ee8;
            text-decoration: underline;
        }
        
        .email-copy:hover {
            color: #2b5be6;
        }
        
        .email-copy-tooltip {
            position: fixed;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 14px;
            pointer-events: none;
            width: 150px;
            text-align: center;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .email-copy-tooltip.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        .email-copy-tooltip:after {
            content: '';
            position: absolute;
            bottom: -6px;
            left: 50%;
            margin-left: -6px;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid rgba(0, 0, 0, 0.8);
        }
    `;
    document.head.appendChild(style);
});