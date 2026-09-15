"""FastAPI application root entrypoint forwarding to backend.main."""

import uvicorn
from backend.main import uvicorn
from core.config import app_settings


def main():
    """Main entrypoint running the Uvicorn ASGI server."""
    uvicorn.run(
        "backend.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.debug,
    )


if __name__ == "__main__":
    main()
