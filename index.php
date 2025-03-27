<?php
// Include autoload for Composer packages (if used)
if (file_exists(__DIR__ . '/vendor/autoload.php')) {
    require __DIR__ . '/vendor/autoload.php';
}

// Set environment variables for InfinityFree
putenv("INFINITYFREE=true");

// Database configuration - replace these placeholders with your actual InfinityFree database credentials
putenv("INFINITYFREE_DB_USER=epiz_username");  // Change this to your actual username
putenv("INFINITYFREE_DB_PASSWORD=db_password"); // Change this to your actual password
putenv("INFINITYFREE_DB_NAME=epiz_dbname"); // Change this to your actual database name
putenv("INFINITYFREE_DB_HOST=sql.infinityfree.com"); // Change this to your actual host

// Secret key for sessions - generate a strong random key
putenv("SESSION_SECRET=change_this_to_a_secure_random_string");

// OpenAI API key if using AI chat feature
putenv("OPENAI_API_KEY=your_openai_api_key"); // Optional: Add if using AI features

// Initialize path handling
$request_uri = $_SERVER['REQUEST_URI'];

// If accessing a static file (CSS, JS, images), serve directly
if (preg_match('/\.(css|js|jpe?g|png|gif|ico|svg|woff2?|ttf|eot)$/', $request_uri)) {
    return false; // Let the server handle it
}

// Check if this is the first run and database needs setup
if ($request_uri == '/setup') {
    include 'initialize_infinityfree.php';
    exit;
}

// Execute the Flask application through the WSGI interface
// Note: This approach uses proc_open which might not work on all shared hosts
// You may need to use a different approach depending on your host's configuration

header('Content-Type: text/html; charset=utf-8');

$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin
   1 => array("pipe", "w"),  // stdout
   2 => array("pipe", "w")   // stderr
);

// Execute the Python script in WSGI mode
$process = proc_open('python3 main.py', $descriptorspec, $pipes, realpath('./'));

if (is_resource($process)) {
    // Close pipes
    fclose($pipes[0]);
    
    // Read output
    $output = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    
    // Read errors
    $errors = stream_get_contents($pipes[2]);
    fclose($pipes[2]);
    
    // Close process
    proc_close($process);
    
    // Output the result
    echo $output;
    
    // Log errors if any
    if (!empty($errors)) {
        $log_file = 'python_error.log';
        file_put_contents($log_file, date('[Y-m-d H:i:s] ') . $errors . PHP_EOL, FILE_APPEND);
        
        // If in debug mode, also show errors
        if (getenv('FLASK_ENV') === 'development') {
            echo "<pre style='color:red;background:#f8f8f8;padding:10px;margin:10px;border:1px solid #ddd;'>";
            echo "Python Error:\n" . htmlspecialchars($errors);
            echo "</pre>";
        }
    }
} else {
    echo "Failed to start Python application. Please check server logs.";
}
?>