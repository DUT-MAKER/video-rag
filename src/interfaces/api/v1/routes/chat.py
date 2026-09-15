"""Chat API routes for conversational AI co-pilot with session memory and streaming SSE."""

import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from src.core.domain.exceptions import DomainValidationError
from src.core.use_cases.chat_with_viral_assistant import ChatWithViralAssistantUseCase
from src.interfaces.api.dependencies import get_chat_assistant_use_case
from src.interfaces.schemas.chat_dtos import (
    ChatMessageResponseDTO,
    ChatRequestDTO,
    ChatResponseDTO,
    SessionDetailResponseDTO,
    SessionListResponseDTO,
)
from src.interfaces.schemas.response_dtos import ReferencedPatternResponseDTO, StandardResponse

router = APIRouter(tags=["Chatbot Co-Pilot"])


@router.post(
    "/chat",
    response_model=StandardResponse[ChatResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Multi-turn conversational turn (Non-streaming)",
)
async def chat_turn(
    request: ChatRequestDTO,
    use_case: ChatWithViralAssistantUseCase = Depends(get_chat_assistant_use_case),
) -> StandardResponse[ChatResponseDTO]:
    """Execute a single conversational turn within a session:
    - Retains multi-turn conversation context.
    - Dynamically retrieves benchmark viral patterns when relevant.
    - Updates and returns assistant response.
    """
    try:
        turn_result = await use_case.execute_turn(
            user_message=request.message,
            session_id=request.session_id,
            top_k_references=request.top_k_references,
        )
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal chat error: {e}",
        ) from e

    data = ChatResponseDTO(
        session_id=turn_result.session_id,
        reply=turn_result.reply,
        role=turn_result.role,
        intent=turn_result.intent,
        referenced_patterns=[
            ReferencedPatternResponseDTO(
                original_caption=r.original_caption,
                matched_hook=r.matched_hook,
                minio_video_url=r.minio_video_url,
                similarity_score=r.similarity_score,
                summary=r.summary,
                image_url=r.image_url,
            )
            for r in turn_result.referenced_patterns
        ],
        created_at=turn_result.created_at,
    )

    return StandardResponse(
        success=True,
        message="Chat response generated successfully.",
        data=data,
    )


@router.post(
    "/chat/stream",
    summary="Multi-turn conversational turn with Server-Sent Events (SSE) streaming",
)
async def chat_stream(
    request: ChatRequestDTO,
    use_case: ChatWithViralAssistantUseCase = Depends(get_chat_assistant_use_case),
) -> StreamingResponse:
    """Stream conversational assistant response tokens in real-time via SSE:
    - Emits initial metadata chunk with session_id, intent, and benchmark references.
    - Emits incremental token events as generated.
    - Emits done event and '[DONE]' signal upon completion.
    """
    clean_msg = request.message.strip()
    if not clean_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User message cannot be empty.",
        )

    async def event_generator() -> AsyncIterator[str]:
        try:
            async for chunk in use_case.execute_streaming(
                user_message=request.message,
                session_id=request.session_id,
                top_k_references=request.top_k_references,
            ):
                if chunk.is_first:
                    metadata_payload = {
                        "event": "metadata",
                        "session_id": chunk.session_id,
                        "intent": chunk.intent.value,
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
        except Exception as err:
            err_payload = {"event": "error", "error": str(err)}
            yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/chat/sessions",
    response_model=StandardResponse[SessionListResponseDTO],
    summary="List all active chat sessions",
)
async def list_chat_sessions(
    use_case: ChatWithViralAssistantUseCase = Depends(get_chat_assistant_use_case),
) -> StandardResponse[SessionListResponseDTO]:
    """Retrieve all active conversation session IDs."""
    sessions = await use_case.list_sessions()
    return StandardResponse(
        success=True,
        message="Chat sessions retrieved.",
        data=SessionListResponseDTO(total_sessions=len(sessions), session_ids=sessions),
    )


@router.get(
    "/chat/sessions/{session_id}",
    response_model=StandardResponse[SessionDetailResponseDTO],
    summary="Get chat session details and message history",
)
async def get_chat_session(
    session_id: str,
    use_case: ChatWithViralAssistantUseCase = Depends(get_chat_assistant_use_case),
) -> StandardResponse[SessionDetailResponseDTO]:
    """Retrieve complete message history and state for a specific session."""
    session = await use_case.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{session_id}' not found.",
        )

    dto_messages = [
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

    current_script_dict = session.current_script.to_dict() if session.current_script else None

    return StandardResponse(
        success=True,
        message="Chat session retrieved.",
        data=SessionDetailResponseDTO(
            session_id=session.session_id,
            message_count=len(session.messages),
            created_at=session.created_at,
            updated_at=session.updated_at,
            messages=dto_messages,
            current_script=current_script_dict,
        ),
    )


@router.delete(
    "/chat/sessions/{session_id}",
    response_model=StandardResponse[dict[str, Any]],
    summary="Delete a chat session",
)
async def delete_chat_session(
    session_id: str,
    use_case: ChatWithViralAssistantUseCase = Depends(get_chat_assistant_use_case),
) -> StandardResponse[dict[str, Any]]:
    """Delete and clear an existing conversation session."""
    deleted = await use_case.delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{session_id}' not found.",
        )

    return StandardResponse(
        success=True,
        message="Chat session deleted successfully.",
        data={"session_id": session_id, "deleted": True},
    )
