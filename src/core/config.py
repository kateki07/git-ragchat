from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"

    # Embedding
    embedding_model: str = "BAAI/bge-small-zh-v1.5"

    # 数据库
    database_url: str = "sqlite:///./ragchat.db"

    # 向量库
    chroma_persist_dir: str = "./chroma_db"

    # 文件上传
    upload_dir: str = "./uploads"

    # 应用
    debug: bool = False


settings = Settings()
