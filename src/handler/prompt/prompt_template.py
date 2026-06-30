from src.core.constant import PROMPT_RAG_SYSTEM_KEY, PROMPT_SYSTEM_KEY
from src.db.pg_db import get_db
from src.services.data_dictionary_service import DataDictionaryService
from langchain_core.prompts import PromptTemplate
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CustomPromptTemplate:
    """カスタムプロンプトテンプレートクラス"""

    def __init__(self):
        pass

    async def _get_system_prompt(self, is_rag: bool = False):
        """DBからシステムプロンプトを取得する"""
        async for db_session in get_db():
            dict_service = DataDictionaryService(db_session)

            dict = await dict_service.get_by_key(
                PROMPT_SYSTEM_KEY if not is_rag else PROMPT_RAG_SYSTEM_KEY
            )
            system_message = dict.value if dict else None

        if not system_message:
            raise ValueError("提示词未设置")

        return system_message

    async def create_prompt(self, is_rag: bool = False):
        """プロンプトテンプレートを生成する"""
        system_prompt = await self._get_system_prompt(is_rag)

        if is_rag:
            prompt_template = system_prompt + """
请根据以下文档回答问题：{context}
问题：{question}
"""
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"],
            )
            return prompt
        else:
            prompt_template = system_prompt + """
问题：{question}
"""
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["question"],
            )
            return prompt
