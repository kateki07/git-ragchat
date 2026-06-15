from sqlalchemy.orm import Session
from src.models.knowledge import KnowledgeSpace, Document, Chunk


class KnowledgeSpaceRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[KnowledgeSpace]:
        return self.db.query(KnowledgeSpace).order_by(KnowledgeSpace.created_at.desc()).all()

    def get_by_id(self, space_id: int) -> KnowledgeSpace | None:
        return self.db.query(KnowledgeSpace).filter(KnowledgeSpace.id == space_id).first()

    def get_by_name(self, name: str) -> KnowledgeSpace | None:
        return self.db.query(KnowledgeSpace).filter(KnowledgeSpace.name == name).first()

    def create(self, name: str, description: str | None) -> KnowledgeSpace:
        space = KnowledgeSpace(name=name, description=description)
        self.db.add(space)
        self.db.commit()
        self.db.refresh(space)
        return space

    def update(self, space: KnowledgeSpace, name: str | None, description: str | None) -> KnowledgeSpace:
        if name is not None:
            space.name = name
        if description is not None:
            space.description = description
        self.db.commit()
        self.db.refresh(space)
        return space

    def delete(self, space: KnowledgeSpace) -> None:
        self.db.delete(space)
        self.db.commit()


class DocumentRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_space(self, space_id: int) -> list[Document]:
        return self.db.query(Document).filter(Document.knowledge_space_id == space_id).all()

    def get_by_id(self, doc_id: int) -> Document | None:
        return self.db.query(Document).filter(Document.id == doc_id).first()

    def create(self, space_id: int, filename: str, file_type: str, file_size: int) -> Document:
        doc = Document(
            knowledge_space_id=space_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            status="pending",
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def update_status(self, doc: Document, status: str, chunk_count: int = 0) -> Document:
        doc.status = status
        doc.chunk_count = chunk_count
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def delete(self, doc: Document) -> None:
        self.db.delete(doc)
        self.db.commit()


class ChunkRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_document(self, doc_id: int) -> list[Chunk]:
        return self.db.query(Chunk).filter(Chunk.document_id == doc_id).order_by(Chunk.chunk_index).all()

    def get_by_ids(self, chunk_ids: list[int]) -> list[Chunk]:
        return self.db.query(Chunk).filter(Chunk.id.in_(chunk_ids)).all()

    def bulk_create(self, space_id: int, doc_id: int, contents: list[str]) -> list[Chunk]:
        chunks = [
            Chunk(
                document_id=doc_id,
                knowledge_space_id=space_id,
                content=content,
                chunk_index=i,
            )
            for i, content in enumerate(contents)
        ]
        self.db.add_all(chunks)
        self.db.commit()
        return chunks

    def delete_by_document(self, doc_id: int) -> None:
        self.db.query(Chunk).filter(Chunk.document_id == doc_id).delete()
        self.db.commit()
