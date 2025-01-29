from dotenv import load_dotenv
import os

# Load environment variables before importing the app
load_dotenv()

from app.main import app

# This allows the application to be run by either Python directly or through Uvicorn
if __name__ == "__main__":
    import uvicorn
    # Use environment variable for port if available (for production), otherwise use 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)