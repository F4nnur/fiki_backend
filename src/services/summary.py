from typing import Sequence
from ..models import Summary, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sa_select
from sqlalchemy import update as sa_update
from ..schemas.summary import SummarySchemaCreate, SummarySchemaUpdate


async def get_by_id(db: AsyncSession, summary_id: int | str) -> Summary | None:
    return await db.get(Summary, summary_id)


async def get_all(db: AsyncSession, bound: int | None = None) -> Sequence[Summary]:
    stmt = sa_select(Summary).limit(bound).order_by(Summary.id)
    return (await db.execute(stmt)).scalars().all()


async def create(db: AsyncSession, summary: SummarySchemaCreate) -> Summary | None:
    payload = summary.dict(exclude_none=True, exclude_unset=True)
    user = await db.get(User, payload["user_id"])
    if not user:
        return None

    db_summary = Summary(**payload)
    db.add(db_summary)
    await db.commit()
    await db.refresh(db_summary)
    return db_summary


async def update(
    db: AsyncSession, payload: SummarySchemaUpdate, summary: Summary
) -> Summary:
    update_data = payload.dict(exclude_none=True, exclude_unset=True)
    query = sa_update(Summary).where(Summary.id == summary.id).values(update_data)
    await db.execute(query)
    await db.commit()
    await db.refresh(summary)
    return summary


async def delete(db: AsyncSession, summary: Summary) -> None:
    await db.delete(summary)
    await db.commit()
