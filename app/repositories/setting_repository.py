"""
Setting repository — key/value store operations
"""
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.other import Setting


class SettingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Setting]:
        result = await self.db.execute(select(Setting).order_by(Setting.key))
        return list(result.scalars().all())

    async def get_by_key(self, key: str) -> Optional[Setting]:
        result = await self.db.execute(
            select(Setting).where(Setting.key == key)
        )
        return result.scalar_one_or_none()

    async def get_by_keys(self, keys: List[str]) -> List[Setting]:
        result = await self.db.execute(
            select(Setting).where(Setting.key.in_(keys)).order_by(Setting.key)
        )
        return list(result.scalars().all())

    async def bulk_upsert(self, data: Dict[str, Optional[str]]) -> None:
        """Insert-or-update each key in a single transaction."""
        for key, value in data.items():
            setting = await self.get_by_key(key)
            if setting:
                setting.value = value
            else:
                self.db.add(Setting(key=key, value=value))
        await self.db.commit()
