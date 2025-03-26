import os
from app import app

if __name__ == "__main__":
    # Check if running on InfinityFree
    if os.environ.get("INFINITYFREE") == "true":
        # When running on InfinityFree, use CGI mode (no separate server)
        print("Content-Type: text/html\n")
        try:
            from wsgiref.handlers import CGIHandler
            CGIHandler().run(app)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    else:
        # For local development
        app.run(host="0.0.0.0", port=5000, debug=True)
