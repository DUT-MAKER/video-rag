"""Search API route."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.use_cases.search_viral_patterns import SearchViralPatternsUseCase
from src.interfaces.api.dependencies import get_search_use_case
from src.interfaces.schemas.request_dtos import SearchPatternsRequestDTO
from src.interfaces.schemas.response_dtos import SearchPatternItem, StandardResponse

router = APIRouter(tags=["Search"])


@router.post(
    "/search-patterns",
    response_model=StandardResponse[list[SearchPatternItem]],
    status_code=status.HTTP_200_OK,
    summary="Semantic similarity search for benchmark viral patterns",
)
async def search_patterns(
    request: SearchPatternsRequestDTO,
    use_case: SearchViralPatternsUseCase = Depends(get_search_use_case),
) -> StandardResponse[list[SearchPatternItem]]:
    """Retrieve benchmark viral videos with similar hook formulas, topics, or storytelling rhythm."""
    try:
        contexts = await use_case.execute(query=request.query, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern search error: {e}",
        ) from e

    items = [
        SearchPatternItem(
            id=ctx.id,
            caption=ctx.caption,
            matched_hook=ctx.hook_candidate,
            summary=ctx.summary,
            video_url=ctx.video_url,
            image_url=ctx.image_url,
            similarity_score=ctx.score,
        )
        for ctx in contexts
    ]

    return StandardResponse(
        success=True,
        message=f"Retrieved {len(items)} matching benchmark patterns.",
        data=items,
    )
