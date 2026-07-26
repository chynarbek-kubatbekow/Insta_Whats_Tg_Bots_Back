from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.club import (
    AdminChangeLog,
    BotSetting,
    ClubApplication,
    KnowledgeEntry,
)


class ClubRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def knowledge_context(self) -> str:
        result = await self.session.execute(
            select(KnowledgeEntry)
            .where(KnowledgeEntry.is_active.is_(True))
            .order_by(KnowledgeEntry.id)
        )
        entries = result.scalars().all()
        return "\n\n".join(f"### {entry.title}\n{entry.content}" for entry in entries)

    async def list_knowledge(self, limit: int = 50, offset: int = 0) -> list[KnowledgeEntry]:
        result = await self.session.execute(
            select(KnowledgeEntry).order_by(KnowledgeEntry.id.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_knowledge(self, entry_id: int) -> KnowledgeEntry | None:
        return await self.session.get(KnowledgeEntry, entry_id)

    async def create_knowledge(self, title: str, content: str) -> KnowledgeEntry:
        entry = KnowledgeEntry(title=title, content=content, category="admin", is_active=True)
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def update_knowledge(
        self, entry_id: int, *, title: str | None = None, content: str | None = None
    ) -> KnowledgeEntry | None:
        entry = await self.get_knowledge(entry_id)
        if entry is None:
            return None
        if title is not None:
            entry.title = title
        if content is not None:
            entry.content = content
        await self.session.flush()
        return entry

    async def toggle_knowledge(self, entry_id: int) -> KnowledgeEntry | None:
        entry = await self.get_knowledge(entry_id)
        if entry is None:
            return None
        entry.is_active = not entry.is_active
        await self.session.flush()
        return entry

    async def delete_knowledge(self, entry_id: int) -> bool:
        entry = await self.get_knowledge(entry_id)
        if entry is None:
            return False
        await self.session.delete(entry)
        await self.session.flush()
        return True

    async def create_application(self, **data: str | None) -> ClubApplication:
        application = ClubApplication(**data)
        self.session.add(application)
        await self.session.flush()
        return application

    async def get_application(self, application_id: int) -> ClubApplication | None:
        return await self.session.get(ClubApplication, application_id)

    async def list_applications(
        self, status: str | None = None, limit: int = 10, offset: int = 0
    ) -> list[ClubApplication]:
        statement = select(ClubApplication).order_by(ClubApplication.id.desc())
        if status:
            statement = statement.where(ClubApplication.status == status)
        result = await self.session.execute(statement.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def count_applications(self, status: str | None = None) -> int:
        statement = select(func.count(ClubApplication.id))
        if status:
            statement = statement.where(ClubApplication.status == status)
        result = await self.session.execute(statement)
        return int(result.scalar_one())

    async def update_application_status(
        self, application_id: int, status: str
    ) -> ClubApplication | None:
        application = await self.get_application(application_id)
        if application is None:
            return None
        application.status = status
        await self.session.flush()
        return application

    async def get_setting(self, key: str, default: str = "") -> str:
        setting = await self.session.get(BotSetting, key)
        return setting.value if setting else default

    async def list_settings(self) -> list[BotSetting]:
        result = await self.session.execute(select(BotSetting).order_by(BotSetting.key))
        return list(result.scalars().all())

    async def get_setting_record(self, key: str) -> BotSetting | None:
        return await self.session.get(BotSetting, key)

    async def update_setting(self, key: str, value: str) -> BotSetting | None:
        setting = await self.get_setting_record(key)
        if setting is None:
            return None
        setting.value = value
        await self.session.flush()
        return setting

    async def log_change(
        self,
        *,
        admin_id: int,
        admin_name: str,
        action: str,
        entity: str,
        entity_id: str = "",
        details: str = "",
    ) -> None:
        self.session.add(
            AdminChangeLog(
                admin_id=str(admin_id),
                admin_name=admin_name,
                action=action,
                entity=entity,
                entity_id=entity_id,
                details=details,
            )
        )
        await self.session.flush()

    async def list_logs(self, limit: int = 15) -> list[AdminChangeLog]:
        result = await self.session.execute(
            select(AdminChangeLog).order_by(AdminChangeLog.id.desc()).limit(limit)
        )
        return list(result.scalars().all())
