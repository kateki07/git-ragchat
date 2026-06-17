import logging
import os
import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import settings
from src.dao.knowledge_dao import CollectionDAO, FileDAO, ChunkDAO
from src.services.vector_service import (
    add_chunks_to_vector_store,
    delete_space_from_vector_store,
    delete_chunks_from_vector_store,
)

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {"pdf", "txt", "docx"}
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _split_text(text: str) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if c]


def _extract_text(file_path: str, extension: str) -> str:
    if extension == "pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if extension == "docx":
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.collection_dao = CollectionDAO(db)
        self.file_dao = FileDAO(db)
        self.chunk_dao = ChunkDAO(db)

    async def list_collections(self):
        return await self.collection_dao.get_all()

    async def get_collection(self, collection_uuid):
        collection = await self.collection_dao.get_by_uuid(collection_uuid)
        if not collection:
            raise HTTPException(status_code=404, detail="知识库不存在")
        return collection

    async def create_collection(self, name: str, cmetadata: dict | None):
        if await self.collection_dao.get_by_name(name):
            raise HTTPException(status_code=400, detail=f"知识库'{name}'已存在")
        return await self.collection_dao.create(name, cmetadata)

    async def update_collection(self, collection_uuid, name: str | None, cmetadata: dict | None):
        collection = await self.get_collection(collection_uuid)
        return await self.collection_dao.update(collection, name, cmetadata)

    async def delete_collection(self, collection_uuid):
        collection = await self.get_collection(collection_uuid)
        delete_space_from_vector_store(collection_uuid)
        await self.collection_dao.delete(collection)

    async def list_files(self, collection_uuid):
        await self.get_collection(collection_uuid)
        return await self.file_dao.get_by_collection(collection_uuid)

    async def upload_and_process(self, collection_uuid, file: UploadFile):
        collection = await self.get_collection(collection_uuid)

        extension = file.filename.rsplit(".", 1)[-1].lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: .{extension}")

        save_dir = os.path.join(settings.upload_dir, str(collection_uuid))
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file.filename)

        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        file_record = await self.file_dao.create(
            collection_id=collection.uuid,
            file_name=file.filename,
            file_extension=extension,
        )

        try:
            text = _extract_text(file_path, extension)
            chunk_texts = _split_text(text)
            chunks = await self.chunk_dao.bulk_create(file_record.uuid, file.filename, chunk_texts)
            add_chunks_to_vector_store(collection_uuid, [str(c.uuid) for c in chunks], chunk_texts)
            logger.info(f"文件'{file.filename}'处理完成，共{len(chunks)}个chunk")
        except Exception as e:
            logger.error(f"文件处理失败: {e}")
            raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

        return file_record
