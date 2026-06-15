import logging
import os
import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.core.config import settings
from src.repositories.knowledge_repo import KnowledgeSpaceRepo, DocumentRepo, ChunkRepo
from src.services.vector_service import (
    add_chunks_to_vector_store,
    delete_space_from_vector_store,
    delete_chunks_from_vector_store,
)

logger = logging.getLogger(__name__)

SUPPORTED_TYPES = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

CHUNK_SIZE = 500      # 每个片段最大字符数
CHUNK_OVERLAP = 50    # 相邻片段重叠字符数（保留上下文连贯性）


def _split_text(text: str) -> list[str]:
    """将长文本切分成带重叠的片段"""
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if c]


def _extract_text(file_path: str, file_type: str) -> str:
    """从不同格式的文件中提取纯文本"""
    if file_type == "application/pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


class KnowledgeService:
    def __init__(self, db: Session):
        self.space_repo = KnowledgeSpaceRepo(db)
        self.doc_repo = DocumentRepo(db)
        self.chunk_repo = ChunkRepo(db)

    def list_spaces(self):
        return self.space_repo.get_all()

    def get_space(self, space_id: int):
        space = self.space_repo.get_by_id(space_id)
        if not space:
            raise HTTPException(status_code=404, detail="知识空间不存在")
        return space

    def create_space(self, name: str, description: str | None):
        if self.space_repo.get_by_name(name):
            raise HTTPException(status_code=400, detail=f"知识空间'{name}'已存在")
        return self.space_repo.create(name, description)

    def update_space(self, space_id: int, name: str | None, description: str | None):
        space = self.get_space(space_id)
        return self.space_repo.update(space, name, description)

    def delete_space(self, space_id: int):
        space = self.get_space(space_id)
        delete_space_from_vector_store(space_id)
        self.space_repo.delete(space)

    def list_documents(self, space_id: int):
        self.get_space(space_id)
        return self.doc_repo.get_by_space(space_id)

    def list_chunks(self, doc_id: int):
        doc = self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文档不存在")
        return self.chunk_repo.get_by_document(doc_id)

    def delete_document(self, doc_id: int):
        doc = self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文档不存在")
        chunk_ids = [c.id for c in self.chunk_repo.get_by_document(doc_id)]
        if chunk_ids:
            delete_chunks_from_vector_store(doc.knowledge_space_id, chunk_ids)
        file_path = os.path.join(settings.upload_dir, str(doc.knowledge_space_id), doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        self.doc_repo.delete(doc)

    async def upload_and_process(self, space_id: int, file: UploadFile):
        self.get_space(space_id)

        if file.content_type not in SUPPORTED_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")

        save_dir = os.path.join(settings.upload_dir, str(space_id))
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file.filename)

        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        doc = self.doc_repo.create(
            space_id=space_id,
            filename=file.filename,
            file_type=file.content_type,
            file_size=len(content),
        )

        try:
            self.doc_repo.update_status(doc, "processing")
            text = _extract_text(file_path, file.content_type)
            chunk_texts = _split_text(text)

            chunks = self.chunk_repo.bulk_create(space_id, doc.id, chunk_texts)
            add_chunks_to_vector_store(space_id, [c.id for c in chunks], chunk_texts)

            self.doc_repo.update_status(doc, "done", chunk_count=len(chunks))
            logger.info(f"文档'{file.filename}'处理完成，共{len(chunks)}个片段")
        except Exception as e:
            self.doc_repo.update_status(doc, "failed")
            logger.error(f"文档处理失败: {e}")
            raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")

        return doc
