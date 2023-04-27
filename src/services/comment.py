from typing import Literal, Sequence
from ..models import Comment, Summary, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sa_select
from sqlalchemy import update as sa_update
from ..schemas.comment import CommentSchemaCreate, CommentSchemaUpdate


async def get_by_id(db: AsyncSession, comment_id: int | str) -> Comment | None:
    return await db.get(Comment, comment_id)


async def get_all(db: AsyncSession, bound: int | None = None) -> Sequence[Comment]:
    stmt = sa_select(Comment).limit(bound).order_by(Comment.id)
    return (await db.execute(stmt)).scalars().all()


async def create(
    db: AsyncSession, comment: CommentSchemaCreate
) -> Comment | Literal["User", "Summary"]:
    payload = comment.dict(exclude_none=True, exclude_unset=True)
    user = await db.get(User, payload["user_id"])
    if not user:
        return "User"

    summary = await db.get(Summary, payload["summary_id"])
    if not summary:
        return "Summary"

    db_comment = Comment(**payload)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def update(
    db: AsyncSession, payload: CommentSchemaUpdate, comment: Comment
) -> Comment:
    update_data = payload.dict(exclude_none=True, exclude_unset=True)
    query = sa_update(Comment).where(Comment.id == comment.id).values(update_data)
    await db.execute(query)
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete(db: AsyncSession, comment: Comment) -> None:
    await db.delete(comment)
    await db.commit()
