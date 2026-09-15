"""Dependency Injection container."""

from functools import lru_cache

from fastapi import Depends
from fastapi.params import Depends as DependsClass

from src.core.ports.chat_session_store_port import IChatSessionStorePort
from src.core.ports.data_reader_port import IDataReaderPort
from src.core.ports.embedding_port import IEmbeddingPort
from src.core.ports.llm_port import ILLMPort
from src.core.ports.vector_store_port import IVectorStorePort
from src.core.use_cases.chat_with_viral_assistant import ChatWithViralAssistantUseCase
from src.core.use_cases.generate_viral_script import GenerateViralScriptUseCase
from src.core.use_cases.ingest_video_data import IngestVideoDataUseCase
from src.core.use_cases.search_viral_patterns import SearchViralPatternsUseCase
from src.infra.config.settings import get_settings
from src.infra.data_readers.json_reader_adapter import JsonDataReaderAdapter
from src.infra.embeddings.self_hosted_embed import SelfHostedEmbeddingAdapter
from src.infra.llm.self_hosted_llm import SelfHostedLLMAdapter
from src.infra.session_store.in_memory_session_store import InMemoryChatSessionAdapter
from src.infra.vector_store.chroma_adapter import ChromaVectorStoreAdapter


@lru_cache
def get_data_reader_adapter() -> IDataReaderPort:
    """Singleton JsonDataReaderAdapter."""
    return JsonDataReaderAdapter()


@lru_cache
def get_embedding_adapter() -> IEmbeddingPort:
    """Singleton SelfHostedEmbeddingAdapter."""
    settings = get_settings()
    return SelfHostedEmbeddingAdapter(
        api_base_url=settings.EMBEDDING_API_BASE_URL,
        api_key=settings.EMBEDDING_API_KEY,
        model_name=settings.EMBEDDING_MODEL_NAME,
        dimension=settings.EMBEDDING_DIMENSION,
        fallback_mode=settings.USE_LOCAL_FALLBACK,
    )


@lru_cache
def get_vector_store_adapter() -> IVectorStorePort:
    """Singleton ChromaVectorStoreAdapter."""
    settings = get_settings()
    return ChromaVectorStoreAdapter(
        persist_dir=settings.CHROMA_PERSIST_DIR,
        collection_name=settings.CHROMA_COLLECTION_NAME,
    )


@lru_cache
def get_llm_adapter() -> ILLMPort:
    """Singleton SelfHostedLLMAdapter."""
    settings = get_settings()
    return SelfHostedLLMAdapter(
        api_base_url=settings.LLM_API_BASE_URL,
        api_key=settings.LLM_API_KEY,
        model_name=settings.LLM_MODEL_NAME,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        fallback_mode=settings.USE_LOCAL_FALLBACK,
    )


def get_ingest_use_case(
    data_reader: IDataReaderPort = Depends(get_data_reader_adapter),
    embedding_port: IEmbeddingPort = Depends(get_embedding_adapter),
    vector_store_port: IVectorStorePort = Depends(get_vector_store_adapter),
) -> IngestVideoDataUseCase:
    """Inject dependencies for IngestVideoDataUseCase (compatible with FastAPI DI and direct invocation)."""
    if isinstance(data_reader, DependsClass):
        data_reader = get_data_reader_adapter()
    if isinstance(embedding_port, DependsClass):
        embedding_port = get_embedding_adapter()
    if isinstance(vector_store_port, DependsClass):
        vector_store_port = get_vector_store_adapter()

    return IngestVideoDataUseCase(
        data_reader=data_reader,
        embedding_port=embedding_port,
        vector_store_port=vector_store_port,
    )


def get_search_use_case(
    embedding_port: IEmbeddingPort = Depends(get_embedding_adapter),
    vector_store_port: IVectorStorePort = Depends(get_vector_store_adapter),
) -> SearchViralPatternsUseCase:
    """Inject dependencies for SearchViralPatternsUseCase (compatible with FastAPI DI and direct invocation)."""
    if isinstance(embedding_port, DependsClass):
        embedding_port = get_embedding_adapter()
    if isinstance(vector_store_port, DependsClass):
        vector_store_port = get_vector_store_adapter()

    return SearchViralPatternsUseCase(
        embedding_port=embedding_port,
        vector_store_port=vector_store_port,
    )


def get_generate_script_use_case(
    llm_port: ILLMPort = Depends(get_llm_adapter),
    embedding_port: IEmbeddingPort = Depends(get_embedding_adapter),
    vector_store_port: IVectorStorePort = Depends(get_vector_store_adapter),
) -> GenerateViralScriptUseCase:
    """Inject dependencies for GenerateViralScriptUseCase (compatible with FastAPI DI and direct invocation)."""
    if isinstance(llm_port, DependsClass):
        llm_port = get_llm_adapter()
    if isinstance(embedding_port, DependsClass):
        embedding_port = get_embedding_adapter()
    if isinstance(vector_store_port, DependsClass):
        vector_store_port = get_vector_store_adapter()

    return GenerateViralScriptUseCase(
        llm_port=llm_port,
        embedding_port=embedding_port,
        vector_store_port=vector_store_port,
    )


@lru_cache
def get_session_store_adapter() -> IChatSessionStorePort:
    """Singleton InMemoryChatSessionAdapter."""
    return InMemoryChatSessionAdapter()


def get_chat_assistant_use_case(
    llm_port: ILLMPort = Depends(get_llm_adapter),
    embedding_port: IEmbeddingPort = Depends(get_embedding_adapter),
    vector_store_port: IVectorStorePort = Depends(get_vector_store_adapter),
    session_store_port: IChatSessionStorePort = Depends(get_session_store_adapter),
) -> ChatWithViralAssistantUseCase:
    """Inject dependencies for ChatWithViralAssistantUseCase (compatible with FastAPI DI and direct invocation)."""
    if isinstance(llm_port, DependsClass):
        llm_port = get_llm_adapter()
    if isinstance(embedding_port, DependsClass):
        embedding_port = get_embedding_adapter()
    if isinstance(vector_store_port, DependsClass):
        vector_store_port = get_vector_store_adapter()
    if isinstance(session_store_port, DependsClass):
        session_store_port = get_session_store_adapter()

    return ChatWithViralAssistantUseCase(
        llm_port=llm_port,
        embedding_port=embedding_port,
        vector_store_port=vector_store_port,
        session_store_port=session_store_port,
    )
