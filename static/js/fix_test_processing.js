
document.addEventListener('DOMContentLoaded', function() {
    // تحسين معالجة رسائل "جاري المعالجة"
    const loadingMessages = document.querySelectorAll('.loading-message');
    loadingMessages.forEach(msg => {
        msg.style.display = 'none';
    });

    // معالجة نماذج توليد الأكواد
    const codeGenForms = document.querySelectorAll('form[action*="generate_lecture_code"]');
    codeGenForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        });
    });

    // معالجة نماذج الاختبارات
    const testForms = document.querySelectorAll('form[action*="/tests/"]');
    testForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
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
