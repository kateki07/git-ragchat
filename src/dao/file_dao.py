import os
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.base_dao import BaseDao
from src.models.knowledge import File
from src.utils.sql_template_manager import SQLTemplateManager


class FileDao(BaseDao):
    """ファイルDAO"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, File, primary_key="uuid")
        self.sql_template_manager = SQLTemplateManager(os.path.dirname(__file__))

    async def get_by_collection(self, collection_id):
        """コレクションIDでファイル一覧を取得する"""
        stmt = select(File).where(File.collection_id == collection_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def query_files(self, collection_id: str = None) -> list[dict]:
        """コレクションIDでファイル一覧をJOINクエリで取得する"""
        try:
            sql = self.sql_template_manager.render_sql("sql/file_query.sql.j2", collection_id=collection_id)
            result = await self.db.execute(text(sql))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return rows
        except FileNotFoundError:
            print("Error: SQL template file 'file_query.sql.j2' not found.")
        except Exception as e:
            print(f"Error executing SQL: {e}")
        return []
