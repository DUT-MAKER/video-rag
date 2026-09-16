"""CLI entrypoint: python -m video_crawler.sessions login <platform>."""

import argparse
import asyncio
from pathlib import Path

from video_crawler.config import get_crawler_settings
from video_crawler.domain import Platform
from video_crawler.infrastructure.sessions import SessionManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an operator-authorized crawler session")
    parser.add_argument("command", choices=["login", "status", "import-cookie-header"])
    parser.add_argument("platform", choices=[item.value for item in Platform])
    parser.add_argument("source", nargs="?", help="Local file containing a copied Cookie header")
    args = parser.parse_args()
    manager = SessionManager(get_crawler_settings())
    platform = Platform(args.platform)
    if args.command == "login":
        path = asyncio.run(manager.login(platform))
        print(f"Session stored at {path.name}")
    elif args.command == "import-cookie-header":
        if not args.source:
            parser.error("import-cookie-header requires a local source file")
        path = manager.import_cookie_header(platform, Path(args.source))
        print(f"Session stored at {path.name}")
    else:
        print(manager.status(platform))


if __name__ == "__main__":
    main()
