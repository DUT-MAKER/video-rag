"""IChatSessionStorePort protocol."""

from typing import Protocol

from src.core.domain.entities.chat_session import ChatSession


class IChatSessionStorePort(Protocol):
    """Protocol for storing and retrieving conversation sessions."""

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Retrieve a chat session by its unique ID."""
        ...

    async def save_session(self, session: ChatSession) -> None:
        """Persist or update an existing chat session."""
        ...

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session by its unique ID."""
        ...

    async def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        ...
