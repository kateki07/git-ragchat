import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.api_contract import APIContract
from src.db.pg_db import get_db
from src.services.file_service import FileService
from src.services.partition_handler import PartitionHandler
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["files"], prefix="/files")

ALLOWED_EXTENSIONS = {".docx", ".pdf"}


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    collection_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """ファイルをアップロードし、チャンク分割・ベクトル化を行う"""
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return APIContract.error(
            message=f"filename: {file.filename}, Unsupported file type. Only .docx and .pdf are allowed.",
            code=400,
        )

    # ファイルをサーバーに保存
    save_dir = os.path.join(settings.upload_dir, collection_id)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)

    try:
        with open(save_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File {file.filename} uploaded successfully.")
    except Exception as e:
        logger.error(f"Failed to save file {file.filename}: {e}")
        return APIContract.error(message=f"Failed to save file {file.filename}: {e}", code=400)

    # ファイルレコードをDBに作成
    file_service = FileService(db)
    file_dto = await file_service.create(
        uuid=uuid.uuid1(),
        file_name=file.filename,
        collection_id=collection_id,
        file_extension=file_extension[1:],
        create_time=datetime.now(timezone.utc),
    )
    logger.info(f"File {file.filename} create file table successfully 信息:{file_dto}")

    # チャンク分割・ベクトル化
    part_handler = PartitionHandler(db)
    await part_handler.file_partition(
        file_id=file_dto.uuid,
        file_name=file.filename,
        file_path=save_path,
        file_extension=file_extension[1:],
        collection_id=collection_id,
    )

    return APIContract.success({"filename": file.filename, "message": "File store to chunk successfully."})


@router.get("/")
async def get_all(
    collection_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """ファイル一覧を取得する"""
    service = FileService(db)
    return APIContract.success(await service.query_files(collection_id))


@router.delete("/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    """ファイルを削除する"""
    service = FileService(db)
    return APIContract.success(await service.delete(file_id))
