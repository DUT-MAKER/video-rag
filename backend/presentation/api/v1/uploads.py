"""Uploads router."""

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, File, UploadFile

from backend.presentation.schemas.user_dtos import PresignUploadInput, UploadOut
from module.upload.use_case.presign_upload import PresignUploadUseCase
from module.upload.use_case.upload_file import UploadFileUseCase

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", response_model=UploadOut)
@inject
async def upload_file(
    use_case: FromDishka[UploadFileUseCase],
    file: UploadFile = File(...),
):
    """Directly upload a file to S3/MinIO."""
    file_bytes = await file.read()
    res = await use_case.execute(
        file_content=file_bytes,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
    )
    return UploadOut(key=res.key, public_url=res.public_url)


@router.post("/presign", response_model=UploadOut)
@inject
async def presign_upload(
    payload: PresignUploadInput,
    use_case: FromDishka[PresignUploadUseCase],
):
    """Generates a presigned URL to upload a file directly to S3/MinIO."""
    res = await use_case.execute(
        key=payload.key,
        content_type=payload.content_type,
    )
    return UploadOut(
        presigned_url=res.presigned_url,
        key=res.key,
        public_url=res.public_url,
    )
