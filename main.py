
from app import app

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True,
        threaded=True,
        # زيادة وقت الانتظار وعدد المحاولات
        request_timeout=300,
        max_retries=3
    )
