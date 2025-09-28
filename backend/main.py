import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path))

from app.main import create_app

# Create the FastAPI app
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
