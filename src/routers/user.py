from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserSchemaCreate, UserSchema
from ..services.user import create, get, get_all
from ..db import get_db
from fastapi_jwt_auth import AuthJWT


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me", response_model=UserSchema)
async def get_current_user(
    db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    db_user = await get(db, current_user)
    return db_user


@users_router.get("", response_model=list[UserSchema], status_code=200)
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
