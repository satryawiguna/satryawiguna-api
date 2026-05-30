"""
Setting service — business logic for key/value settings
"""
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.setting_repository import SettingRepository


class SettingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.setting_repository = SettingRepository(db)

    async def get_all_settings(self) -> Dict[str, Optional[str]]:
        settings = await self.setting_repository.get_all()
        return {s.key: s.value for s in settings}

    async def update_settings(
        self, data: Dict[str, Optional[str]]
    ) -> Dict[str, Optional[str]]:
        await self.setting_repository.bulk_upsert(data)
        return await self.get_all_settings()

    async def get_settings_by_keys(
        self, keys: List[str]
    ) -> Dict[str, Optional[str]]:
        settings = await self.setting_repository.get_by_keys(keys)
        return {s.key: s.value for s in settings}
