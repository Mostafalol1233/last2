document.addEventListener('DOMContentLoaded', function() {
    // إذا كان هناك زر بدء الاختبار، أضف مستمع حدث للنقر
    const startTestButtons = document.querySelectorAll('a[href*="start_test"]');
    
    if (startTestButtons.length > 0) {
        startTestButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // إظهار رسالة للمستخدم
                const loadingText = document.createElement('span');
                loadingText.className = 'ms-2 spinner-text';
                loadingText.textContent = 'جاري بدء الاختبار...';
                
                // إضافة أيقونة تحميل
                const loadingSpinner = document.createElement('span');
                loadingSpinner.className = 'spinner-border spinner-border-sm ms-2';
                loadingSpinner.setAttribute('role', 'status');
                loadingSpinner.setAttribute('aria-hidden', 'true');
                
                // إضافة العناصر إلى الزر
                button.appendChild(loadingSpinner);
                button.appendChild(loadingText);
                
                // السماح بالانتقال العادي بعد عرض الرسالة
                setTimeout(() => {
                    return true;
                }, 500);
            });
        });
    }
    
    // إذا كنا في صفحة أخذ الاختبار
    if (window.location.href.includes('/student/tests/take/')) {
        // إعادة توجيه الصفحة تلقائيًا إذا ظلت في وضع المعالجة
        setTimeout(() => {
            const processingIndicator = document.querySelector('.test-processing');
            if (processingIndicator) {
                window.location.reload();
            }
        }, 3000);
    }
});
