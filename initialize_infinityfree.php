<?php
// Setup page for the InfinityFree hosting
header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إعداد منصة الأستاذ أحمد حلي</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f7f9fc;
            margin: 0;
            padding: 20px;
            direction: rtl;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #fff;
            padding: 20px 30px;
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }
        .step {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
            border-right: 4px solid #3498db;
        }
        .step h2 {
            margin-top: 0;
            color: #3498db;
        }
        .log {
            background: #f1f1f1;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 13px;
            overflow-x: auto;
            color: #444;
            margin: 10px 0;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .btn {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 15px;
            cursor: pointer;
            text-align: center;
        }
        .btn:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>إعداد منصة الأستاذ أحمد حلي</h1>
        
        <?php
        // Check if submitted form
        $submitted = isset($_POST['setup']);
        $success = false;
        
        if ($submitted) {
            // Get credentials from form
            $db_user = $_POST['db_user'] ?? '';
            $db_password = $_POST['db_password'] ?? '';
            $db_name = $_POST['db_name'] ?? '';
            $db_host = $_POST['db_host'] ?? '';
            $session_key = $_POST['session_key'] ?? '';
            $openai_key = $_POST['openai_key'] ?? '';
            
            // Save credentials to environment
            putenv("INFINITYFREE=true");
            putenv("INFINITYFREE_DB_USER=$db_user");
            putenv("INFINITYFREE_DB_PASSWORD=$db_password");
            putenv("INFINITYFREE_DB_NAME=$db_name");
            putenv("INFINITYFREE_DB_HOST=$db_host");
            putenv("SESSION_SECRET=$session_key");
            if (!empty($openai_key)) {
                putenv("OPENAI_API_KEY=$openai_key");
            }
            
            // Check if we can update the index.php file with these credentials
            $index_file = file_get_contents('index.php');
            
            // Replace the placeholders in index.php
            $index_file = preg_replace('/putenv\("INFINITYFREE_DB_USER=.*?"\);/', 'putenv("INFINITYFREE_DB_USER='.$db_user.'");', $index_file);
            $index_file = preg_replace('/putenv\("INFINITYFREE_DB_PASSWORD=.*?"\);/', 'putenv("INFINITYFREE_DB_PASSWORD='.$db_password.'");', $index_file);
            $index_file = preg_replace('/putenv\("INFINITYFREE_DB_NAME=.*?"\);/', 'putenv("INFINITYFREE_DB_NAME='.$db_name.'");', $index_file);
            $index_file = preg_replace('/putenv\("INFINITYFREE_DB_HOST=.*?"\);/', 'putenv("INFINITYFREE_DB_HOST='.$db_host.'");', $index_file);
            $index_file = preg_replace('/putenv\("SESSION_SECRET=.*?"\);/', 'putenv("SESSION_SECRET='.$session_key.'");', $index_file);
            
            // Update OpenAI key if provided
            if (!empty($openai_key)) {
                $index_file = preg_replace('/putenv\("OPENAI_API_KEY=.*?"\);/', 'putenv("OPENAI_API_KEY='.$openai_key.'");', $index_file);
            }
            
            // Save the updated index.php file
            if (is_writable('index.php')) {
                file_put_contents('index.php', $index_file);
                echo '<div class="success">تم تحديث ملف index.php بالإعدادات الجديدة بنجاح!</div>';
            } else {
                echo '<div class="error">تعذر الكتابة إلى ملف index.php. تأكد من صلاحيات الملف.</div>';
            }
            
            try {
                // Create database connection
                $conn = new mysqli($db_host, $db_user, $db_password, $db_name);
                
                // Check connection
                if ($conn->connect_error) {
                    throw new Exception("فشل الاتصال بقاعدة البيانات: " . $conn->connect_error);
                }
                
                echo '<div class="success">تم الاتصال بقاعدة البيانات بنجاح!</div>';
                
                // Create/update database tables using Python script
                echo '<div class="step"><h2>إنشاء جداول قاعدة البيانات</h2>';
                $db_output = shell_exec('python3 -c "from app import app, db; with app.app_context(): db.create_all(); print(\'تم إنشاء جداول قاعدة البيانات بنجاح\')"');
                
                if ($db_output) {
                    echo '<div class="success">تم إنشاء جداول قاعدة البيانات بنجاح!</div>';
                    echo '<div class="log">' . nl2br(htmlspecialchars($db_output)) . '</div>';
                } else {
                    echo '<div class="error">حدث خطأ أثناء إنشاء جداول قاعدة البيانات.</div>';
                }
                echo '</div>';
                
                // Create default admin user
                echo '<div class="step"><h2>إنشاء المستخدمين الافتراضيين</h2>';
                $user_output = shell_exec('python3 create_users.py');
                
                if ($user_output) {
                    echo '<div class="success">تم إنشاء المستخدمين الافتراضيين بنجاح!</div>';
                    echo '<div class="log">' . nl2br(htmlspecialchars($user_output)) . '</div>';
                } else {
                    echo '<div class="error">حدث خطأ أثناء إنشاء المستخدمين الافتراضيين.</div>';
                }
                echo '</div>';
                
                $conn->close();
                $success = true;
                
            } catch (Exception $e) {
                echo '<div class="error">خطأ: ' . $e->getMessage() . '</div>';
            }
        }
        
        // Show completion message or setup form
        if ($success) {
            echo '<div class="step"><h2>تم الإعداد بنجاح!</h2>';
            echo '<p>تم تهيئة المنصة بنجاح. يمكنك الآن استخدام المنصة.</p>';
            echo '<p>بيانات تسجيل الدخول الافتراضية للمسؤول:</p>';
            echo '<p>اسم المستخدم: <strong>admin</strong><br>كلمة المرور: <strong>admin123</strong></p>';
            echo '<p class="warning">ملاحظة مهمة: يرجى تغيير كلمة المرور الافتراضية بعد تسجيل الدخول لأول مرة!</p>';
            echo '<a href="/" class="btn">الذهاب إلى الصفحة الرئيسية</a>';
            echo '</div>';
        } else {
            // Setup form
            ?>
            <form method="post" action="/setup">
                <div class="step">
                    <h2>إعدادات قاعدة البيانات</h2>
                    <p>أدخل بيانات اتصال قاعدة البيانات الخاصة باستضافة InfinityFree:</p>
                    
                    <div>
                        <label for="db_user">اسم مستخدم قاعدة البيانات:</label>
                        <input type="text" id="db_user" name="db_user" required style="width: 100%; padding: 8px; margin: 5px 0 15px;">
                    </div>
                    
                    <div>
                        <label for="db_password">كلمة مرور قاعدة البيانات:</label>
                        <input type="password" id="db_password" name="db_password" required style="width: 100%; padding: 8px; margin: 5px 0 15px;">
                    </div>
                    
                    <div>
                        <label for="db_name">اسم قاعدة البيانات:</label>
                        <input type="text" id="db_name" name="db_name" required style="width: 100%; padding: 8px; margin: 5px 0 15px;">
                    </div>
                    
                    <div>
                        <label for="db_host">مضيف قاعدة البيانات:</label>
                        <input type="text" id="db_host" name="db_host" value="sql.infinityfree.com" required style="width: 100%; padding: 8px; margin: 5px 0 15px;">
                    </div>
                </div>
                
                <div class="step">
                    <h2>إعدادات الأمان</h2>
                    <div>
                        <label for="session_key">مفتاح الجلسة (مفتاح عشوائي آمن):</label>
                        <input type="text" id="session_key" name="session_key" value="<?php echo bin2hex(random_bytes(24)); ?>" required style="width: 100%; padding: 8px; margin: 5px 0 15px;">
                    </div>
                </div>
                
                <div class="step">
                    <h2>إعدادات اختيارية</h2>
                    <div>
                        <label for="openai_key">مفتاح API الخاص بـ OpenAI (اختياري، لميزة الدردشة الذكية):</label>
                        <input type="text" id="openai_key" name="openai_key" style="width: 100%; padding: 8px; margin: 5px 0 15px;">
                    </div>
                </div>
                
                <input type="submit" name="setup" value="بدء الإعداد" class="btn" style="width: 100%;">
            </form>
            <?php
        }
        ?>
    </div>
</body>
</html>