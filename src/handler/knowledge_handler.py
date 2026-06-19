import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.pg_db import get_db
from src.services.knowledge_service import KnowledgeService
from src.dto.knowledge_dto import (
    CollectionCreate, CollectionUpdate, CollectionOut, FileOut,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def get_service(db: AsyncSession = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)


@router.get("/collections", response_model=list[CollectionOut])
async def list_collections(svc: KnowledgeService = Depends(get_service)):
    return await svc.list_collections()


@router.post("/collections", response_model=CollectionOut)
async def create_collection(body: CollectionCreate, svc: KnowledgeService = Depends(get_service)):
    return await svc.create_collection(body.name, body.cmetadata)


@router.put("/collections/{collection_uuid}", response_model=CollectionOut)
async def update_collection(collection_uuid: uuid.UUID, body: CollectionUpdate, svc: KnowledgeService = Depends(get_service)):
    return await svc.update_collection(collection_uuid, body.name, body.cmetadata)


@router.delete("/collections/{collection_uuid}")
async def delete_collection(collection_uuid: uuid.UUID, svc: KnowledgeService = Depends(get_service)):
    await svc.delete_collection(collection_uuid)
    return {"message": "已删除"}


@router.get("/collections/{collection_uuid}/files", response_model=list[FileOut])
async def list_files(collection_uuid: uuid.UUID, svc: KnowledgeService = Depends(get_service)):
    return await svc.list_files(collection_uuid)


@router.post("/collections/{collection_uuid}/files", response_model=FileOut)
async def upload_file(
    collection_uuid: uuid.UUID,
    file: UploadFile = File(...),
    svc: KnowledgeService = Depends(get_service),
):
    return await svc.upload_and_process(collection_uuid, file)
