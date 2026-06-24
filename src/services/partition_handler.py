from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.concurrency import run_in_threadpool
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.dao.chunk_dao import ChunkDao
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PartitionHandler:
    """ファイルを分割してチャンクを作成するハンドラ（ベクトル化はスケジューラーが担当）"""

    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

    def __init__(self, db: AsyncSession):
        self.chunk_dao = ChunkDao(db)

    def _load_document(self, file_path: str, file_extension: str) -> list[str]:
        """ファイルからテキストを抽出する"""
        if file_extension == "pdf":
            loader = PyMuPDFLoader(file_path)
            docs = loader.load()
            return [doc.page_content for doc in docs]
        elif file_extension in ("doc", "docx"):
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
            return [doc.page_content for doc in docs]
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return [f.read()]

    def _split_texts(self, texts: list[str]) -> list[str]:
        """テキストをチャンクに分割する"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP,
        )
        all_chunks = []
        for text in texts:
            all_chunks.extend(splitter.split_text(text))
        return [c for c in all_chunks if c.strip()]

    async def file_partition(
        self,
        file_id,
        file_name: str,
        file_path: str,
        file_extension: str,
        collection_id=None,
    ):
        """ファイルを分割してチャンク（status=0）をDBに保存する"""
        logger.info(f"ファイル分割開始: {file_name}")

        raw_texts = await run_in_threadpool(self._load_document, file_path, file_extension)
        chunk_texts = self._split_texts(raw_texts)
        logger.info(f"チャンク数: {len(chunk_texts)}")

        if not chunk_texts:
            logger.warning(f"ファイル '{file_name}' からテキストを抽出できませんでした")
            return

        await self.chunk_dao.bulk_create(file_id, file_name, chunk_texts)
        logger.info(f"チャンク保存完了: {file_name}, {len(chunk_texts)}件")
