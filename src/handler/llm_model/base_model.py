from abc import ABC, abstractmethod


class BaseModel(ABC):
    """LLMモデルの抽象基底クラス"""

    @abstractmethod
    async def init_llm_model(self):
        pass
