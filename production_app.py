import os
from app import app, socketio

# Production configuration
class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    DEBUG = False
    TESTING = False

app.config.from_object(ProductionConfig)

if __name__ == '__main__':
    # Get port from environment variable (for platforms like Heroku)
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting production server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=False) 