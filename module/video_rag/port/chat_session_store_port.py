"""IChatSessionStorePort protocol."""

from typing import Protocol

from module.video_rag.domain.entities.chat_session import ChatSession


class IChatSessionStorePort(Protocol):
    """Protocol for persisting and retrieving multi-turn chat sessions."""

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Fetch session by ID. Returns None if session does not exist."""
        ...

    async def save_session(self, session: ChatSession) -> None:
        """Persist or update chat session state."""
        ...

    async def delete_session(self, session_id: str) -> bool:
        """Remove session from storage."""
        ...

    async def list_sessions(self, limit: int = 50) -> list[ChatSession]:
        """List active sessions sorted by last updated timestamp."""
        ...
