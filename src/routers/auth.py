from fastapi import APIRouter, Depends, HTTPException
from src.config import settings
from fastapi_jwt_auth import AuthJWT
from ..schemas.auth import AuthSchemaIn, AuthSchemaOut
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from ..services.user import get_with_paswd

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@AuthJWT.load_config
def get_config():
    return settings


@auth_router.post("/login", response_model=AuthSchemaOut)
async def login(
    user_data: AuthSchemaIn,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    db_user = await get_with_paswd(db, user_data.username, user_data.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = authorize.create_access_token(subject=user_data.username)
    refresh_token = authorize.create_refresh_token(subject=user_data.username)
    return {"access_token": access_token, "refresh_token": refresh_token}
