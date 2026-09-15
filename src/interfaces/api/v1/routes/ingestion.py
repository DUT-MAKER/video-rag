"""Ingestion API route."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.domain.exceptions import VideoRecordParsingError
from src.core.use_cases.ingest_video_data import IngestVideoDataUseCase
from src.interfaces.api.dependencies import get_ingest_use_case
from src.interfaces.schemas.request_dtos import IngestRequestDTO
from src.interfaces.schemas.response_dtos import IngestionResponseData, StandardResponse

router = APIRouter(tags=["Ingestion"])


@router.post(
    "/ingest",
    response_model=StandardResponse[IngestionResponseData],
    status_code=status.HTTP_200_OK,
    summary="Ingest viral video knowledge into RAG system",
)
async def ingest_videos(
    request: IngestRequestDTO,
    use_case: IngestVideoDataUseCase = Depends(get_ingest_use_case),
) -> StandardResponse[IngestionResponseData]:
    """Ingest viral video knowledge from a JSON file path or raw records list:
    1. Normalizes fields (caption, transcript, image_url, summary, video_url).
    2. Extracts opening 3-5 second hook candidates.
    3. Generates vector embeddings and indexes records into ChromaDB.
    """
    if not request.file_path and not request.records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'file_path' or 'records' list must be provided in request body.",
        )

    source = request.file_path if request.file_path else request.records

    try:
        result = await use_case.execute(source=source)  # type: ignore[arg-type]
    except VideoRecordParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data ingestion error: {e}",
        ) from e

    return StandardResponse(
        success=True,
        message=f"Successfully ingested {result.total_indexed}/{result.total_processed} videos into knowledge store.",
        data=IngestionResponseData(
            total_processed=result.total_processed,
            total_indexed=result.total_indexed,
            extracted_hooks=result.extracted_hooks,
            indexed_ids=result.indexed_ids,
        ),
    )
