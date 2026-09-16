class DomainError(Exception):
    """Base domain exception."""

    pass


class DomainValidationError(DomainError):
    """Domain validation error."""

    pass


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


class EmbeddingError(DomainError):
    """Error occurred during text embedding generation."""

    pass


class RerankError(DomainError):
    """Error occurred during document reranking."""

    pass


class MediaExtractionError(DomainError):
    """Error occurred during audio/frame extraction from video."""

    pass


class TranscriptionError(DomainError):
    """Error occurred during speech transcription or speaker diarization."""

    pass
