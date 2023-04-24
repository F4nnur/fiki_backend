from typing import Sequence
from ..models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sa_select
from sqlalchemy import update as sa_update
from ..schemas.user import UserSchemaCreate, UserSchemaUpdate
from ..security import get_password_hash, verify_password


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    query = sa_select(User).where(User.username == username)
    return (await db.execute(query)).scalar_one_or_none()


async def get_by_id(db: AsyncSession, user_id: int | str) -> User | None:
    return await db.get(User, user_id)


async def get_with_paswd(
    db: AsyncSession, username: str, raw_password: str
) -> User | None:
    db_user = (
        await db.execute(sa_select(User).where((User.username == username)))
    ).scalar()
    if not db_user or not verify_password(raw_password, db_user.hashed_password):
        return None
    return db_user


async def get_all(db: AsyncSession, bound: int | None = None) -> Sequence[User]:
    stmt = sa_select(User).limit(bound).order_by(User.id)
    return (await db.execute(stmt)).scalars().all()


async def create(db: AsyncSession, user: UserSchemaCreate) -> User | None:
    if await get_by_username(db, user.username):
        return None
    hashed_password = get_password_hash(user.password)
    payload = user.dict()
    del payload["password"]
    db_user = User(**payload, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update(db: AsyncSession, payload: UserSchemaUpdate, user: User) -> User:
    update_data = payload.dict(
        exclude_none=True, exclude_unset=True, exclude_defaults=True
    )
    if update_data.get("password"):
        hashed_passwd = get_password_hash(update_data.get("password"))
        update_data["hashed_password"] = hashed_passwd
        update_data.pop("password")

    query = sa_update(User).where(User.username == user.username).values(update_data)
    await db.execute(query)
    await db.commit()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()
