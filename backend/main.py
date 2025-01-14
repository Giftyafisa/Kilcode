import uvicorn
import os
from app.main import app
from ssl_config import setup_ssl

if __name__ == "__main__":
    # Set up SSL and CORS
    ssl_context, ssl_cert_path, ssl_key_path = setup_ssl(app)
    
    # Production settings
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=ssl_key_path,
        ssl_certfile=ssl_cert_path,
        workers=4,  # Number of worker processes
        log_level="info",
        reload=False,  # Disable auto-reload in production
        proxy_headers=True,  # Enable proxy headers
        forwarded_allow_ips="*"  # Allow forwarded IPs
    ) 