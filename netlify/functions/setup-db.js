const { execSync } = require('child_process');

/**
 * Netlify function to set up the database schema.
 * This function executes the Python script to initialize the database.
 * 
 * URL: /.netlify/functions/setup-db
 */
exports.handler = async function(event, context) {
  try {
    // Execute the database setup script with DATABASE_URL from environment variables
    const result = execSync('python setup_neon_db.py').toString();
    
    return {
      statusCode: 200,
      body: JSON.stringify({ 
        message: 'Database initialization complete', 
        details: result,
        success: true
      })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        message: 'Error during database initialization', 
        error: error.toString(),
        success: false
      })
    };
  }
};