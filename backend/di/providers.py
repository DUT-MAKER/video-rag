from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import (
    embedding_settings,
    llm_settings,
    rerank_settings,
    vector_store_settings,
)
from module.auth.infra.repositories.users import UserRepository
from module.auth.port.user_repo import IUserRepository
from module.auth.use_case.get_profile import GetProfileUseCase
from module.auth.use_case.login import LoginUseCase
from module.auth.use_case.register import RegisterUseCase
from module.auth.use_case.update_profile import UpdateProfileUseCase
from module.upload.infra.clients.s3_client import S3Client
from module.upload.port.s3_client import IS3Client
from module.upload.use_case.presign_upload import PresignUploadUseCase
from module.upload.use_case.upload_file import UploadFileUseCase
from module.video_rag.infra.data_readers.json_reader_adapter import (
    JsonDataReaderAdapter,
)
from module.video_rag.infra.embeddings.self_hosted_embed import (
    SelfHostedEmbeddingAdapter,
)
from module.video_rag.infra.llm.self_hosted_llm import SelfHostedLLMAdapter
from module.video_rag.infra.rerank.dut_ai_rerank_adapter import DutAiRerankAdapter
from module.video_rag.infra.session_store.in_memory_session_store import (
    InMemoryChatSessionAdapter,
)
from module.video_rag.infra.vector_store.pgvector_adapter import PgVectorAdapter
from module.video_rag.port.chat_session_store_port import IChatSessionStorePort
from module.video_rag.port.data_reader_port import IDataReaderPort
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.llm_port import ILLMPort
from module.video_rag.port.rerank_port import IRerankPort
from module.video_rag.port.vector_store_port import IVectorStorePort
from module.video_rag.use_case.chat_with_viral_assistant import (
    ChatWithViralAssistantUseCase,
)
from module.video_rag.use_case.generate_viral_script import GenerateViralScriptUseCase
from module.video_rag.use_case.search_viral_patterns import SearchViralPatternsUseCase


class DatabaseSessionProvider(Provider):
    """Provides per-request database sessions with automatic commit."""

    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterable[AsyncSession]:
        from backend.di.database import async_session_factory

        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


class AuthModuleProvider(Provider):
    """Dishka provider for Auth module."""

    scope = Scope.REQUEST

    @provide
    def user_repository(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session=session)

    @provide
    def register_use_case(self, repo: IUserRepository) -> RegisterUseCase:
        return RegisterUseCase(user_repo=repo)

    @provide
    def login_use_case(self, repo: IUserRepository) -> LoginUseCase:
        return LoginUseCase(user_repo=repo)

    @provide
    def get_profile_use_case(self, repo: IUserRepository) -> GetProfileUseCase:
        return GetProfileUseCase(user_repo=repo)

    @provide
    def update_profile_use_case(self, repo: IUserRepository) -> UpdateProfileUseCase:
        return UpdateProfileUseCase(user_repo=repo)


class UploadModuleProvider(Provider):
    """Dishka provider for Upload module."""

    scope = Scope.REQUEST

    @provide
    def s3_client(self) -> IS3Client:
        return S3Client()

    @provide
    def upload_file_use_case(self, s3_client: IS3Client) -> UploadFileUseCase:
        return UploadFileUseCase(s3_client=s3_client)

    @provide
    def presign_upload_use_case(self, s3_client: IS3Client) -> PresignUploadUseCase:
        return PresignUploadUseCase(s3_client=s3_client)


class VideoRagModuleProvider(Provider):
    """Dishka provider for Video RAG module."""

    scope = Scope.APP

    @provide
    def embedding_port(self) -> IEmbeddingPort:
        return SelfHostedEmbeddingAdapter(
            api_base_url=embedding_settings.api_base_url,
            api_key=embedding_settings.api_key,
            model_name=embedding_settings.model_name,
            dimension=embedding_settings.dimension,
        )

    @provide
    def llm_port(self) -> ILLMPort:
        return SelfHostedLLMAdapter(
            api_base_url=llm_settings.api_base_url,
            api_key=llm_settings.api_key,
            model_name=llm_settings.model_name,
            temperature=llm_settings.temperature,
            max_tokens=llm_settings.max_tokens,
        )

    @provide
    def data_reader_port(self) -> IDataReaderPort:
        return JsonDataReaderAdapter()

    @provide
    def vector_store_port(self) -> IVectorStorePort:
        from backend.di.database import async_engine

        return PgVectorAdapter(
            engine=async_engine,
            table_name=vector_store_settings.table_name,
            dimension=embedding_settings.dimension,
        )

    @provide
    def chat_session_store_port(self) -> IChatSessionStorePort:
        return InMemoryChatSessionAdapter()

    @provide
    def rerank_port(self) -> IRerankPort:
        return DutAiRerankAdapter(
            api_base_url=rerank_settings.api_base_url,
            api_key=rerank_settings.api_key,
            model_name=rerank_settings.model_name,
            timeout=rerank_settings.timeout,
        )

    @provide(scope=Scope.REQUEST)
    def search_use_case(
        self,
        embedding_port: IEmbeddingPort,
        vector_store: IVectorStorePort,
        rerank_port: IRerankPort,
    ) -> SearchViralPatternsUseCase:
        return SearchViralPatternsUseCase(
            embedding_port=embedding_port,
            vector_store_port=vector_store,
            rerank_port=rerank_port if rerank_settings.enabled else None,
            candidate_k=rerank_settings.candidate_k,
        )

    @provide(scope=Scope.REQUEST)
    def generate_use_case(
        self,
        embedding_port: IEmbeddingPort,
        vector_store: IVectorStorePort,
        llm_port: ILLMPort,
        rerank_port: IRerankPort,
    ) -> GenerateViralScriptUseCase:
        return GenerateViralScriptUseCase(
            embedding_port=embedding_port,
            vector_store_port=vector_store,
            llm_port=llm_port,
            rerank_port=rerank_port if rerank_settings.enabled else None,
            candidate_k=rerank_settings.candidate_k,
        )

    @provide(scope=Scope.REQUEST)
    def chat_use_case(
        self,
        chat_store: IChatSessionStorePort,
        embedding_port: IEmbeddingPort,
        vector_store: IVectorStorePort,
        llm_port: ILLMPort,
        rerank_port: IRerankPort,
    ) -> ChatWithViralAssistantUseCase:
        return ChatWithViralAssistantUseCase(
            session_store_port=chat_store,
            embedding_port=embedding_port,
            vector_store_port=vector_store,
            llm_port=llm_port,
            rerank_port=rerank_port if rerank_settings.enabled else None,
            candidate_k=rerank_settings.candidate_k,
        )
