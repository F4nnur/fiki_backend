from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserSchemaCreate, UserSchemaUpdate, UserSchema
from ..schemas.summary import SummaryUserSchema
from ..schemas.comment import CommentUserSchema
from ..services.user import create, get_by_id, get_all, update, get_by_username, delete
from ..db import get_db
from fastapi_jwt_auth import AuthJWT


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me", response_model=UserSchema)
async def get_current_user(
    db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    db_user = await get_by_username(db, current_user)
    if not db_user:
        raise HTTPException(status_code=401)
    return db_user


@users_router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user = await get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router.get("", response_model=list[UserSchema])
async def get_users(
    db: AsyncSession = Depends(get_db),
    limit: int | None = None,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    return await get_all(db, limit)


@users_router.post("", response_model=UserSchema, status_code=201)
async def create_user(user: UserSchemaCreate, db: AsyncSession = Depends(get_db)):
    new_user = await create(db, user)
    if not new_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return new_user


@users_router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    payload: UserSchemaUpdate,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    username = authorize.get_jwt_subject()
    user_claims = authorize.get_raw_jwt()["user_claims"]

    if not user_claims["id"] == user_id:
        raise HTTPException(status_code=405)

    new_user_data: dict = payload.dict()
    if not any(new_user_data.values()):
        raise HTTPException(status_code=400)

    existed_user = await get_by_username(db, username=username)

    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    return await update(db, payload, existed_user)


@users_router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_claims = authorize.get_raw_jwt()["user_claims"]

    if not user_claims["id"] == user_id:
        raise HTTPException(status_code=405)

    existed_user = await get_by_id(db, user_id)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    return await delete(db, existed_user)


@users_router.get("/{user_id}/summaries", response_model=list[SummaryUserSchema])
async def get_user_summaries(
    user_id: int, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user = await get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.summaries


@users_router.get("/{user_id}/comments", response_model=list[CommentUserSchema])
async def get_user_comments(
    user_id: int, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user = await get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.comments
