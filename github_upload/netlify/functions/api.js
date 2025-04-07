const serverless = require("serverless-http");
const { spawn } = require("child_process");
const path = require("path");

// Start the Flask app as a subprocess
const flask = spawn("python", [path.join(__dirname, "../../main.py")]);

// Log Flask output
flask.stdout.on("data", (data) => {
  console.log(`Flask: ${data}`);
});

flask.stderr.on("data", (data) => {
  console.error(`Flask error: ${data}`);
});

// Export the serverless handler
const handler = serverless(flask);
module.exports = { handler };