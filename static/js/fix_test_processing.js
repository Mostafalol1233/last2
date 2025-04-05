document.addEventListener('DOMContentLoaded', function() {
    // منع النسخ في صفحة الاختبار
    if (window.location.href.includes('/student/tests/take/') || window.location.href.includes('/attempt/')) {
        // منع النسخ
        document.addEventListener('copy', function(e) {
            e.preventDefault();
            return false;
        });

        // منع اللصق
        document.addEventListener('paste', function(e) {
            e.preventDefault();
            return false;
        });

        // منع السحب
        document.addEventListener('dragstart', function(e) {
            e.preventDefault();
            return false;
        });

        // منع النقر بزر الماوس الأيمن
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });

        // منع اختيار النص
        document.addEventListener('selectstart', function(e) {
            e.preventDefault();
            return false;
        });
    }
});