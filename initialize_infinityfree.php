<?php
// Set environment variables for InfinityFree
putenv("INFINITYFREE=true");

// Database configuration (add your database credentials here)
putenv("INFINITYFREE_DB_USER=your_db_username");
putenv("INFINITYFREE_DB_PASSWORD=your_db_password");
putenv("INFINITYFREE_DB_NAME=your_db_name");
putenv("INFINITYFREE_DB_HOST=your_db_host"); // Often something like sql312.infinityfree.com

// Connect to the database
$db_user = getenv("INFINITYFREE_DB_USER");
$db_password = getenv("INFINITYFREE_DB_PASSWORD");
$db_name = getenv("INFINITYFREE_DB_NAME");
$db_host = getenv("INFINITYFREE_DB_HOST");

try {
    // Create connection
    $conn = new mysqli($db_host, $db_user, $db_password, $db_name);
    
    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    echo "Database connection successful!<br>";
    
    // Execute a Python script to create database tables
    $output = shell_exec('python3 -c "from app import app, db; with app.app_context(): db.create_all(); print(\'Database tables created successfully\')"');
    echo $output;
    
    // Create default users
    $output = shell_exec('python3 create_users.py');
    echo $output;
    
    $conn->close();
    echo "Database initialization completed!";
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
?>