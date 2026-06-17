import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDAO
from src.models.knowledge import Collection, File, Chunk


class CollectionDAO(BaseDAO):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Collection)

    async def get_all(self) -> list[Collection]:
        result = await self.db.execute(
            select(Collection).order_by(Collection.create_time.desc())
        )
        return result.scalars().all()

    async def get_by_uuid(self, collection_uuid: uuid.UUID) -> Collection | None:
        result = await self.db.execute(
            select(Collection).filter(Collection.uuid == collection_uuid)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Collection | None:
        result = await self.db.execute(
            select(Collection).filter(Collection.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, cmetadata: dict | None = None) -> Collection:
        collection = Collection(name=name, cmetadata=cmetadata)
        self.db.add(collection)
        await self.db.commit()
        await self.db.refresh(collection)
        return collection

    async def update(self, collection: Collection, name: str | None, cmetadata: dict | None) -> Collection:
        if name is not None:
            collection.name = name
        if cmetadata is not None:
            collection.cmetadata = cmetadata
        await self.db.commit()
        await self.db.refresh(collection)
        return collection


class FileDAO(BaseDAO):
    def __init__(self, db: AsyncSession):
        super().__init__(db, File)

    async def get_by_uuid(self, file_uuid: uuid.UUID) -> File | None:
        result = await self.db.execute(
            select(File).filter(File.uuid == file_uuid)
        )
        return result.scalar_one_or_none()

    async def get_by_collection(self, collection_id: uuid.UUID) -> list[File]:
        result = await self.db.execute(
            select(File).filter(File.collection_id == collection_id)
        )
        return result.scalars().all()

    async def create(self, collection_id: uuid.UUID, file_name: str, file_extension: str, cmetadata: dict | None = None) -> File:
        file = File(
            collection_id=collection_id,
            file_name=file_name,
            file_extension=file_extension,
            cmetadata=cmetadata,
        )
        self.db.add(file)
        await self.db.commit()
        await self.db.refresh(file)
        return file


class ChunkDAO(BaseDAO):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Chunk)

    async def get_by_file(self, file_id: uuid.UUID) -> list[Chunk]:
        result = await self.db.execute(
            select(Chunk).filter(Chunk.file_id == file_id).order_by(Chunk.index)
        )
        return result.scalars().all()

    async def bulk_create(self, file_id: uuid.UUID, file_name: str, contexts: list[str]) -> list[Chunk]:
        chunks = [
            Chunk(
                file_id=file_id,
                file_name=file_name,
                context=context,
                index=i,
                status=0,
            )
            for i, context in enumerate(contexts)
        ]
        self.db.add_all(chunks)
        await self.db.commit()
        return chunks

    async def update_status(self, chunk: Chunk, status: int) -> None:
        chunk.status = status
        await self.db.commit()
