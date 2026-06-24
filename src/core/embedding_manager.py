import os
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

_embeddings = None


async def initialize_embeddings() -> None:
    """アプリ起動時に埋め込みモデルをシングルトンで初期化する"""
    global _embeddings
    try:
        model_path = settings.embedding_model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"埋め込みモデルロード開始: device={device}")

        if device == "cuda":
            model_kwargs = {"device": device}
            encode_kwargs = {"normalize_embeddings": True}
        else:
            model_kwargs = {"device": device, "trust_remote_code": True}
            encode_kwargs = {"normalize_embeddings": True, "batch_size": 32}
            if hasattr(torch, "set_num_threads"):
                torch.set_num_threads(os.cpu_count())

        _embeddings = HuggingFaceEmbeddings(
            model_name=model_path,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )
        logger.info(f"埋め込みモデル初期化成功: {model_path}, device={device}")
    except Exception as e:
        logger.error(f"埋め込みモデル初期化失敗: {e}")
        raise


def get_embeddings() -> HuggingFaceEmbeddings:
    """初期化済み埋め込みモデルを返す"""
    global _embeddings
    if _embeddings is None:
        raise RuntimeError(
            "埋め込みモデルが未初期化です。initialize_embeddings()を先に呼び出してください。"
        )
    return _embeddings
