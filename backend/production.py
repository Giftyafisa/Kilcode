from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import ssl
import os
from app.main import app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_production_app():
    # CORS settings for production
    origins = [
        "https://kilcode.vercel.app",  # Your Vercel frontend
        "https://ng.kilcode.duckdns.org",
        "https://gh.kilcode.duckdns.org",
        "http://localhost:5173",  # For local development
        "http://localhost:3000"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

if __name__ == "__main__":
    production_app = setup_production_app()
    
    # SSL Configuration
    ssl_certfile = os.path.join(os.path.dirname(__file__), "ssl", "fullchain.pem")
    ssl_keyfile = os.path.join(os.path.dirname(__file__), "ssl", "privkey.pem")
    
    # Create SSL directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), "ssl"), exist_ok=True)
    
    # Check if SSL certificates exist
    if not (os.path.exists(ssl_certfile) and os.path.exists(ssl_keyfile)):
        print("SSL certificates not found. Running without SSL...")
        uvicorn.run(production_app, host="0.0.0.0", port=8000)
    else:
        print("Running with SSL...")
        uvicorn.run(
            production_app,
            host="0.0.0.0",
            port=8000,
            ssl_certfile=ssl_certfile,
            ssl_keyfile=ssl_keyfile
        ) 