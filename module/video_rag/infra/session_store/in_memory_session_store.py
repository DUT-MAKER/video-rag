"""InMemoryChatSessionAdapter implementation."""

import asyncio
from typing import Any

from module.video_rag.domain.entities.chat_session import ChatSession
from module.video_rag.port.chat_session_store_port import IChatSessionStorePort


class InMemoryChatSessionAdapter(IChatSessionStorePort):
    """Thread-safe in-memory adapter for storing and managing conversation sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, ChatSession] = {}
        self._lock = asyncio.Lock()

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Retrieve a chat session by its unique ID."""
        async with self._lock:
            return self._sessions.get(session_id)

    async def save_session(self, session: ChatSession) -> None:
        """Persist or update an existing chat session."""
        async with self._lock:
            self._sessions[session.session_id] = session

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session by its unique ID. Returns True if deleted."""
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    async def list_sessions(self, limit: int = 50) -> list[Any]:
        """List all active sessions."""
        async with self._lock:
            sessions = list(self._sessions.values())
            sessions.sort(key=lambda s: s.updated_at, reverse=True)
            return sessions[:limit]

    async def clear_all(self) -> None:
        """Clear all stored sessions (useful for tests)."""
        async with self._lock:
            self._sessions.clear()
