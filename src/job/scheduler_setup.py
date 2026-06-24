import asyncio
import time
import uuid
from datetime import datetime, timezone

from src.core.embedding_manager import get_embeddings
from src.db.pg_db import get_db
from src.dto.embedding_dto import EmbeddingDto
from src.services.chunk_service import ChunkService
from src.services.embedding_service import EmbeddingService
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def do_embedding_chunks():
    """ベクトル化待ちチャンクを取得してエンベディングを生成・保存する"""
    rows = []
    async for session in get_db():
        chunk_service = ChunkService(session)
        rows = await chunk_service.query_embedding_chunks()
        if not rows:
            logger.info("ベクトル化待ちデータなし")
            return []

    logger.info(f"ベクトル化待ちデータ取得成功: {len(rows)}件")

    embedding_model = get_embeddings()

    chunk_embedding_dict = await _create_embeddings(rows, embedding_model)
    logger.info(f"ベクトル化完了: {len(chunk_embedding_dict)}件")

    embedding_dto_list = await _prepare_embedding_list(rows, chunk_embedding_dict)
    logger.info(f"EmbeddingDTO準備完了: {len(embedding_dto_list)}件")

    async for session in get_db():
        embedding_service = EmbeddingService(session)
        await embedding_service.batch_embedding_create(embedding_dto_list)

        chunk_service = ChunkService(session)
        await chunk_service.batch_update_status_by_uuids(
            [row.chunk_id for row in rows], 1
        )


async def _prepare_embedding_list(chunk_embedding_dtos, embeddings_dict) -> list[EmbeddingDto]:
    """EmbeddingDTOリストを組み立てる"""
    embedding_dto_list = []
    for dto in chunk_embedding_dtos:
        embedding_dto = EmbeddingDto(
            uuid=uuid.uuid4(),
            chunk_id=dto.chunk_id,
            collection_id=dto.collection_id,
            file_id=dto.file_id,
            embedding_vector=embeddings_dict[dto.chunk_id],
            search_vector=None,
            cmetadata=None,
            create_time=datetime.now(timezone.utc),
        )
        embedding_dto_list.append(embedding_dto)
    return embedding_dto_list


async def _create_embeddings(chunk_embedding_dtos, embeddings_model) -> dict:
    """チャンクテキストをベクトル化し {chunk_id: vector} 辞書を返す"""
    start_time = time.time()

    texts = [row.context for row in chunk_embedding_dtos]
    chunk_ids = [row.chunk_id for row in chunk_embedding_dtos]

    if not texts:
        return {}

    embeddings = embeddings_model.embed_documents(texts)
    embeddings_dict = dict(zip(chunk_ids, embeddings))

    total_time = time.time() - start_time
    logger.info(f"ベクトル化所要時間: {total_time:.2f}秒")

    return embeddings_dict


async def scheduled_job():
    """10秒ごとにエンベディングジョブを実行するバックグラウンドスケジューラー"""
    try:
        while True:
            logger.info("定期ジョブ実行中...")
            try:
                await do_embedding_chunks()
            except Exception as e:
                logger.error(f"定期ジョブでエラーが発生しました: {e}", exc_info=True)
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        logger.info("定期ジョブがキャンセルされました")
        raise
