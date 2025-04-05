
document.addEventListener('DOMContentLoaded', function() {
    // تعطيل جميع رسائل "جاري المعالجة"
    const loadingMessages = document.querySelectorAll('.loading-message');
    loadingMessages.forEach(msg => {
        msg.style.display = 'none';
    });

    // تمكين جميع الأزرار في النماذج
    const allForms = document.querySelectorAll('form');
    allForms.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('disabled');
        }
    });

    // إعادة تمكين النموذج بعد الإرسال
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.classList.remove('disabled');
            }
        });
    });

    // منع النسخ في صفحة الاختبار
    if (window.location.href.includes('/student/tests/take/') || 
        window.location.href.includes('/attempt/') || 
        window.location.href.includes('/test/')) {
        
        document.addEventListener('copy', function(e) {
            e.preventDefault();
            return false;
        });

        document.addEventListener('paste', function(e) {
            e.preventDefault();
            return false;
        });

        document.addEventListener('dragstart', function(e) {
            e.preventDefault();
            return false;
        });

        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });

        document.addEventListener('selectstart', function(e) {
            e.preventDefault();
            return false;
        });
    }
});
