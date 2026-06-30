from langchain_core.messages import AIMessage
from src.core.constant import LLM_MODEL
from src.db.pg_db import get_db
from src.handler.llm_model.llm_factory import LLMFactory
from src.handler.prompt.prompt_template import CustomPromptTemplate
from src.services.data_dictionary_service import DataDictionaryService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChatModelHandler:
    """LLMチェーンの初期化と会話処理を担当するハンドラー"""

    def __init__(self):
        pass

    async def _init_llm(self):
        """DBからモデル種別を読み取り、LLMインスタンスを初期化する"""
        llm_model = None
        async for db_session in get_db():
            dict_service = DataDictionaryService(db_session)
            dict = await dict_service.get_by_key(LLM_MODEL)
            llm_model = dict.value if dict else None

        if llm_model is None:
            raise Exception("LLM_MODEL not found")

        # ファクトリーでモデルインスタンスを生成する
        llm_instance = LLMFactory.create_model(llm_model)
        return await llm_instance.init_llm_model()

    async def init_chain(self, is_rag: bool = False):
        """プロンプトとLLMを結合したチェーンを返す"""
        llm = await self._init_llm()
        prompt = await CustomPromptTemplate().create_prompt(is_rag)
        chain = prompt | llm
        return chain

    async def get_llm_response(self, user_id: str, message: str) -> dict | None:
        """通常モードでLLMの回答を取得する"""
        chain = await self.init_chain(False)

        response = await chain.ainvoke({"question": message})
        result = {}
        # レスポンスの型を確認してコンテンツを取得する
        if isinstance(response, AIMessage):
            result["content"] = response.content
        else:
            raise ValueError("AI大模型返回的不是 AIMessage 类型")

        return result
