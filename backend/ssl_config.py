from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ssl
import os

def setup_ssl(app: FastAPI):
    # CORS settings
    origins = [
        "https://kilcode.vercel.app",
        "https://ng.kilcode.duckdns.org",
        "https://gh.kilcode.duckdns.org",
        "http://localhost:5173",
        "http://localhost:3000"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # SSL Context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_cert_path = os.path.join(os.path.dirname(__file__), "ssl", "cert.pem")
    ssl_key_path = os.path.join(os.path.dirname(__file__), "ssl", "key.pem")
    
    return ssl_context, ssl_cert_path, ssl_key_path 