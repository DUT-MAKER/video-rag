"""Dependency injection package.

Keep package initialization lightweight so the crawler worker can import the
shared database module without constructing all API providers.
"""
