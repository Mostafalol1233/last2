<?php
// Set environment variables for InfinityFree
putenv("INFINITYFREE=true");

// Database configuration (add your database credentials here)
putenv("INFINITYFREE_DB_USER=your_db_username");
putenv("INFINITYFREE_DB_PASSWORD=your_db_password");
putenv("INFINITYFREE_DB_NAME=your_db_name");
putenv("INFINITYFREE_DB_HOST=your_db_host"); // Often something like sql312.infinityfree.com

// Secret key for session
putenv("SESSION_SECRET=your_secret_key");

// Execute the Python application through CGI
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin
   1 => array("pipe", "w"),  // stdout
   2 => array("pipe", "w")   // stderr
);

// Execute the Python script
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
        file_put_contents('error.log', $errors, FILE_APPEND);
    }
}
?>