"""FastAPI application root entrypoint forwarding to backend.main."""

import uvicorn

from backend.main import app
from core.config import app_settings

__all__ = ["app", "main"]



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
