from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.services.knowledge_service import KnowledgeService
from src.schemas.knowledge import (
    KnowledgeSpaceCreate, KnowledgeSpaceUpdate,
    KnowledgeSpaceOut, DocumentOut, ChunkOut,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def get_service(db: Session = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)


@router.get("/spaces", response_model=list[KnowledgeSpaceOut])
def list_spaces(svc: KnowledgeService = Depends(get_service)):
    return svc.list_spaces()


@router.post("/spaces", response_model=KnowledgeSpaceOut)
def create_space(body: KnowledgeSpaceCreate, svc: KnowledgeService = Depends(get_service)):
    return svc.create_space(body.name, body.description)


@router.put("/spaces/{space_id}", response_model=KnowledgeSpaceOut)
def update_space(space_id: int, body: KnowledgeSpaceUpdate, svc: KnowledgeService = Depends(get_service)):
    return svc.update_space(space_id, body.name, body.description)


@router.delete("/spaces/{space_id}")
def delete_space(space_id: int, svc: KnowledgeService = Depends(get_service)):
    svc.delete_space(space_id)
    return {"message": "已删除"}


@router.get("/spaces/{space_id}/documents", response_model=list[DocumentOut])
def list_documents(space_id: int, svc: KnowledgeService = Depends(get_service)):
    return svc.list_documents(space_id)


@router.post("/spaces/{space_id}/documents", response_model=DocumentOut)
async def upload_document(
    space_id: int,
    file: UploadFile = File(...),
    svc: KnowledgeService = Depends(get_service),
):
    return await svc.upload_and_process(space_id, file)


@router.get("/documents/{doc_id}/chunks", response_model=list[ChunkOut])
def list_chunks(doc_id: int, svc: KnowledgeService = Depends(get_service)):
    return svc.list_chunks(doc_id)


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, svc: KnowledgeService = Depends(get_service)):
    svc.delete_document(doc_id)
    return {"message": "已删除"}
