from langchain_deepseek import ChatDeepSeek
from src.core.constant import DEEPSEEK_API_KEY, TEMPERATURE
from src.db.pg_db import get_db
from src.handler.llm_model.base_model import BaseModel
from src.services.data_dictionary_service import DataDictionaryService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DeepSeekModel(BaseModel):
    """LangChainのDeepSeekを使用してレスポンスを生成するモデル"""

    def __init__(self):
        self.llm = None

    async def init_llm_model(self):
        """DeepSeek LLMモデルを初期化する"""
        logger.info("ChatDeepSeek init_llm_model")
        api_key = None
        temperature = "0.5"

        async for db_session in get_db():
            dict_service = DataDictionaryService(db_session)

            dict_key = await dict_service.get_by_key(DEEPSEEK_API_KEY)
            api_key = dict_key.value if dict_key else None

            dict_temp = await dict_service.get_by_key(TEMPERATURE)
            temperature = dict_temp.value if dict_temp else "0.5"

        logger.info(f"DeepSeek api_key取得完了")

        if api_key:
            self.llm = ChatDeepSeek(
                model="deepseek-chat",
                api_key=api_key,
                temperature=float(temperature),
            )
        else:
            logger.error("DeepSeek api_key is None")

        return self.llm
