from langchain_openai import ChatOpenAI
from src.core.constant import OPENAI_API_BASE, OPENAI_API_KEY, TEMPERATURE
from src.db.pg_db import get_db
from src.handler.llm_model.base_model import BaseModel
from src.services.data_dictionary_service import DataDictionaryService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIModel(BaseModel):
    """LangChainのOpenAIを使用してレスポンスを生成するモデル"""

    def __init__(self):
        self.llm = None

    async def init_llm_model(self):
        """OpenAI LLMモデルを初期化する"""
        logger.info("OpenAIModel init_llm_model")
        openai_api_key = None
        openai_base_url = None
        temperature = "0.5"

        async for db_session in get_db():
            dict_service = DataDictionaryService(db_session)

            dict_key = await dict_service.get_by_key(OPENAI_API_KEY)
            openai_api_key = dict_key.value if dict_key else None

            dict_base = await dict_service.get_by_key(OPENAI_API_BASE)
            openai_base_url = dict_base.value if dict_base else None

            dict_temp = await dict_service.get_by_key(TEMPERATURE)
            temperature = dict_temp.value if dict_temp else "0.5"

        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured in the database.")

        self.llm = ChatOpenAI(
            model="gpt-4",
            api_key=openai_api_key,
            base_url=openai_base_url,
            temperature=float(temperature),
        )

        return self.llm
