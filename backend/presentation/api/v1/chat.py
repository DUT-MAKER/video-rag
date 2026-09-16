"""Chat and Conversational Assistant router."""

import json
from collections.abc import AsyncIterator

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from backend.presentation.schemas.chat_dtos import (
    ChatMessageResponseDTO,
    ChatRequestDTO,
    ChatResponseDTO,
    SessionDetailResponseDTO,
    SessionListResponseDTO,
)
from backend.presentation.schemas.response_dtos import (
    ReferencedPatternResponseDTO,
    StandardResponse,
)
from module.video_rag.domain.exceptions import SessionNotFoundError
from module.video_rag.use_case.chat_with_viral_assistant import (
    ChatWithViralAssistantUseCase,
)

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


async def _sse_stream_generator(
    use_case: ChatWithViralAssistantUseCase,
    payload: ChatRequestDTO,
) -> AsyncIterator[str]:
    """Format domain streaming chunks into Server-Sent Events (SSE)."""
    async for chunk in use_case.execute_streaming(
        user_message=payload.message,
        session_id=payload.session_id,
        top_k_references=payload.top_k_references,
    ):
        if chunk.is_first:
            metadata_payload = {
                "event": "metadata",
                "session_id": chunk.session_id,
                "intent": chunk.intent.value if chunk.intent else "general_chat",
                "referenced_patterns": [
                    {
                        "original_caption": r.original_caption,
                        "matched_hook": r.matched_hook,
                        "minio_video_url": r.minio_video_url,
                        "similarity_score": r.similarity_score,
                        "summary": r.summary,
                        "image_url": r.image_url,
                    }
                    for r in chunk.referenced_patterns
                ],
            }
            yield f"data: {json.dumps(metadata_payload, ensure_ascii=False)}\n\n"
        elif chunk.is_done:
            done_payload = {
                "event": "done",
                "session_id": chunk.session_id,
            }
            yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        else:
            token_payload = {
                "event": "token",
                "session_id": chunk.session_id,
                "token": chunk.token,
            }
            yield f"data: {json.dumps(token_payload, ensure_ascii=False)}\n\n"



@router.post(
    "/stream",
    response_class=StreamingResponse,
    summary="Stream conversational assistant responses via Server-Sent Events (SSE)",
)
@inject
async def chat_stream(
    payload: ChatRequestDTO,
    use_case: FromDishka[ChatWithViralAssistantUseCase],
) -> StreamingResponse:
    """Stream response tokens in real-time."""
    return StreamingResponse(
        _sse_stream_generator(use_case, payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "",
    response_model=StandardResponse[ChatResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Synchronous conversational assistant turn",
)
@inject
async def chat_turn(
    payload: ChatRequestDTO,
    use_case: FromDishka[ChatWithViralAssistantUseCase],
) -> StandardResponse[ChatResponseDTO]:
    """Complete non-streaming conversational turn."""
    result = await use_case.execute_turn(
        user_message=payload.message,
        session_id=payload.session_id,
        top_k_references=payload.top_k_references,
    )

    data = ChatResponseDTO(
        session_id=result.session_id,
        reply=result.reply,
        role=result.role,
        intent=result.intent,
        referenced_patterns=[
            ReferencedPatternResponseDTO(
                original_caption=r.original_caption,
                matched_hook=r.matched_hook,
                minio_video_url=r.minio_video_url,
                similarity_score=r.similarity_score,
                summary=r.summary,
                image_url=r.image_url,
            )
            for r in result.referenced_patterns
        ],
        created_at=result.created_at,
    )

    return StandardResponse(
        success=True,
        message="Assistant response generated successfully.",
        data=data,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=StandardResponse[SessionDetailResponseDTO],
    summary="Retrieve session history",
)
@inject
async def get_session_history(
    session_id: str,
    use_case: FromDishka[ChatWithViralAssistantUseCase],
) -> StandardResponse[SessionDetailResponseDTO]:
    """Retrieve full conversation history for a session."""
    session = await use_case.get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session with ID '{session_id}' not found.")

    messages_dto = [
        ChatMessageResponseDTO(
            role=m.role,
            content=m.content,
            timestamp=m.timestamp,
            referenced_patterns=[
                ReferencedPatternResponseDTO(
                    original_caption=r.original_caption,
                    matched_hook=r.matched_hook,
                    minio_video_url=r.minio_video_url,
                    similarity_score=r.similarity_score,
                    summary=r.summary,
                    image_url=r.image_url,
                )
                for r in m.referenced_patterns
            ],
        )
        for m in session.messages
    ]

    return StandardResponse(
        success=True,
        message="Session history retrieved successfully.",
        data=SessionDetailResponseDTO(
            session_id=session.session_id,
            message_count=len(session.messages),
            created_at=session.created_at,
            updated_at=session.updated_at,
            messages=messages_dto,
            current_script=session.current_script.to_dict() if session.current_script else None,
        ),
    )


@router.delete(
    "/sessions/{session_id}",
    response_model=StandardResponse[dict[str, object]],
    summary="Delete a chat session",
)

@inject
async def delete_chat_session(
    session_id: str,
    use_case: FromDishka[ChatWithViralAssistantUseCase],
) -> StandardResponse[dict[str, object]]:
    """Delete session by ID."""
    deleted = await use_case.delete_session(session_id)
    if not deleted:
        raise SessionNotFoundError(f"Session with ID '{session_id}' not found.")

    return StandardResponse(
        success=True,
        message=f"Session '{session_id}' deleted successfully.",
        data={"session_id": session_id, "deleted": True},
    )



@router.get(
    "/sessions",
    response_model=StandardResponse[SessionListResponseDTO],
    summary="List active conversation sessions",
)
@inject
async def list_chat_sessions(
    use_case: FromDishka[ChatWithViralAssistantUseCase],
) -> StandardResponse[SessionListResponseDTO]:
    """List active session IDs."""
    sessions = await use_case.list_sessions()
    session_ids = [s.session_id if hasattr(s, "session_id") else str(s) for s in sessions]

    return StandardResponse(
        success=True,
        message=f"Found {len(session_ids)} active sessions.",
        data=SessionListResponseDTO(
            total_sessions=len(session_ids),
            session_ids=session_ids,
        ),
    )
