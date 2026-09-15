"""Video RAG domain exceptions."""

from core.exceptions import DomainError, DomainValidationError


class VideoRecordParsingError(DomainError):
    """Error parsing raw video records from data sources."""
    pass


class ScriptGenerationError(DomainError):
    """Error occurred during viral script generation or parsing."""
    pass


class VectorStoreError(DomainError):
    """Error occurred during vector store operations."""
    pass


class SessionNotFoundError(DomainError):
    """Error when requested chat session does not exist."""
    pass
