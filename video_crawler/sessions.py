"""CLI entrypoint: python -m video_crawler.sessions login <platform>."""

import argparse
import asyncio

from video_crawler.config import get_crawler_settings
from video_crawler.domain import Platform
from video_crawler.infrastructure.sessions import SessionManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an operator-authorized crawler session")
    parser.add_argument("command", choices=["login", "status"])
    parser.add_argument("platform", choices=[item.value for item in Platform])
    args = parser.parse_args()
    manager = SessionManager(get_crawler_settings())
    platform = Platform(args.platform)
    if args.command == "login":
        path = asyncio.run(manager.login(platform))
        print(f"Session stored at {path.name}")
    else:
        print(manager.status(platform))


if __name__ == "__main__":
    main()
