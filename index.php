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

// Configure logging
$log_dir = __DIR__ . '/logs';
if (!is_dir($log_dir)) {
    mkdir($log_dir, 0755, true);
}
putenv("LOG_DIR={$log_dir}");

// Initialize path handling
$request_uri = $_SERVER['REQUEST_URI'];

// Handle health check requests
if ($request_uri == '/ping' || $request_uri == '/health') {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'ok', 'timestamp' => time()]);
    exit;
}

// Implement basic caching for static assets
$cache_control_max_age = 86400; // 24 hours
if (preg_match('/\.(css|js|jpe?g|png|gif|ico|svg|woff2?|ttf|eot)$/', $request_uri)) {
    $file_path = __DIR__ . ($request_uri[0] === '/' ? $request_uri : '/' . $request_uri);
    if (file_exists($file_path)) {
        $mime_types = [
            'css' => 'text/css',
            'js' => 'application/javascript',
            'jpg' => 'image/jpeg',
            'jpeg' => 'image/jpeg',
            'png' => 'image/png',
            'gif' => 'image/gif',
            'ico' => 'image/x-icon',
            'svg' => 'image/svg+xml',
            'woff' => 'font/woff',
            'woff2' => 'font/woff2',
            'ttf' => 'font/ttf',
            'eot' => 'application/vnd.ms-fontobject'
        ];
        
        $ext = pathinfo($file_path, PATHINFO_EXTENSION);
        if (isset($mime_types[$ext])) {
            header('Content-Type: ' . $mime_types[$ext]);
            header('Cache-Control: public, max-age=' . $cache_control_max_age);
            header('Expires: ' . gmdate('D, d M Y H:i:s', time() + $cache_control_max_age) . ' GMT');
            readfile($file_path);
            exit;
        }
    }
    return false; // Let the server handle it as a fallback
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

// Add security headers
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');
header('X-XSS-Protection: 1; mode=block');

// Add basic request rate limiting (simple implementation)
session_start();
$rate_limit_window = 60; // 1 minute
$rate_limit_max = 60;    // 60 requests per minute

$current_time = time();
$session_key = 'rate_limit_data';

if (!isset($_SESSION[$session_key])) {
    $_SESSION[$session_key] = [
        'count' => 1,
        'window_start' => $current_time
    ];
} else {
    $rate_data = $_SESSION[$session_key];
    
    // Check if we're in a new window
    if ($current_time - $rate_data['window_start'] > $rate_limit_window) {
        // Reset for new window
        $_SESSION[$session_key] = [
            'count' => 1,
            'window_start' => $current_time
        ];
    } else {
        // Increment counter
        $_SESSION[$session_key]['count']++;
        
        // Check if limit exceeded
        if ($_SESSION[$session_key]['count'] > $rate_limit_max) {
            header('HTTP/1.1 429 Too Many Requests');
            header('Retry-After: ' . ($rate_limit_window - ($current_time - $rate_data['window_start'])));
            echo 'Rate limit exceeded. Please try again later.';
            exit;
        }
    }
}

$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin
   1 => array("pipe", "w"),  // stdout
   2 => array("pipe", "w")   // stderr
);

// Execute the Python script in WSGI mode
// Use timeout to prevent hanging processes
$cwd = realpath('./');
$timeout = 30; // 30 seconds timeout
$env = $_ENV;

// Add timeout prevention
set_time_limit($timeout + 5);

// Execute the Python script
$process = proc_open('python3 main.py', $descriptorspec, $pipes, $cwd, $env);

if (is_resource($process)) {
    // Set non-blocking mode for output pipe
    stream_set_blocking($pipes[1], 0);
    stream_set_blocking($pipes[2], 0);
    
    // Close input pipe as we don't need it
    fclose($pipes[0]);
    
    // Initialize variables
    $output = '';
    $error = '';
    $start_time = time();
    
    // Read with timeout
    while (time() - $start_time < $timeout) {
        $read = array($pipes[1], $pipes[2]);
        $write = null;
        $except = null;
        
        // Check if there's data to read (with 1 second timeout)
        if (stream_select($read, $write, $except, 1)) {
            foreach ($read as $pipe) {
                if ($pipe === $pipes[1]) {
                    $output .= fread($pipe, 8192);
                } elseif ($pipe === $pipes[2]) {
                    $error .= fread($pipe, 8192);
                }
            }
        }
        
        // Check if process is still running
        $status = proc_get_status($process);
        if (!$status['running']) {
            // Process finished, get any remaining output
            $output .= stream_get_contents($pipes[1]);
            $error .= stream_get_contents($pipes[2]);
            break;
        }
    }
    
    // Close pipes
    fclose($pipes[1]);
    fclose($pipes[2]);
    
    // Terminate the process if it's still running (timeout occurred)
    $status = proc_get_status($process);
    if ($status['running']) {
        // Force kill the process
        proc_terminate($process, 9); // SIGKILL
        proc_close($process);
        
        // Return timeout error
        header('HTTP/1.1 504 Gateway Timeout');
        echo '<h1>504 Gateway Timeout</h1><p>The application took too long to respond.</p>';
        
        // Log the timeout
        $log_file = $log_dir . '/timeout_error.log';
        file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Request timeout for: {$request_uri}" . PHP_EOL, FILE_APPEND);
        exit;
    } else {
        // Close the process handle
        proc_close($process);
    }
    
    // Output the result
    echo $output;
    
    // Log errors if any
    if (!empty($error)) {
        $log_file = $log_dir . '/python_error.log';
        file_put_contents($log_file, date('[Y-m-d H:i:s] ') . $error . PHP_EOL, FILE_APPEND);
        
        // If in debug mode, also show errors
        if (getenv('FLASK_DEBUG') === 'true') {
            echo "<pre style='color:red;background:#f8f8f8;padding:10px;margin:10px;border:1px solid #ddd;'>";
            echo "Python Error:\n" . htmlspecialchars($error);
            echo "</pre>";
        } else {
            // For production errors, log but show a friendly message
            if (strpos($error, 'Error: 500') !== false) {
                include __DIR__ . '/templates/500.html';
            }
        }
    }
} else {
    // Failed to start the process
    header('HTTP/1.1 500 Internal Server Error');
    include __DIR__ . '/templates/500.html';
    
    // Log the error
    $log_file = $log_dir . '/startup_error.log';
    file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Failed to start Python application." . PHP_EOL, FILE_APPEND);
}
?>