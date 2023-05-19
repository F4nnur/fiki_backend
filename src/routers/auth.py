from fastapi import APIRouter, Depends, HTTPException
from src.config import settings
from fastapi_jwt_auth import AuthJWT
from ..schemas.auth import AuthSchemaIn, AuthSchemaOut, RefreshAccessToken
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from ..services.user import get_with_paswd, get_by_id
from ..redis import RedisClient


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
redis_conn = RedisClient().conn


@AuthJWT.load_config
def get_config():
    return settings


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token: str) -> bool:
    jti = decrypted_token["jti"]
    entry = redis_conn.get(jti)
    return entry and entry == "true"


@auth_router.post("/login", response_model=AuthSchemaOut)
async def login(
    user_data: AuthSchemaIn,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    db_user = await get_with_paswd(db, user_data.username, user_data.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")

    user_claims = {"user_claims": {"id": db_user.id, "role": db_user.role.name}}
    access_token = authorize.create_access_token(
        subject=user_data.username, user_claims=user_claims
    )
    refresh_token = authorize.create_refresh_token(
        subject=user_data.username, user_claims=user_claims
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/refresh", response_model=RefreshAccessToken)
async def refresh_access_token(
    db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_refresh_token_required()
    user_claims = {"user_claims": authorize.get_raw_jwt()["user_claims"]}
    current_user = await get_by_id(db, user_claims["user_claims"]["id"])
    jti = authorize.get_raw_jwt()["jti"]

    new_access_token = authorize.create_access_token(
        subject=current_user.username, user_claims=user_claims
    )

    redis_conn.setex(jti, settings.AUTHJWT_REFRESH_TOKEN_EXPIRES, "true")
    return {"access_token": new_access_token}


@auth_router.delete("/logout")
async def logout(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    jti = authorize.get_raw_jwt()["jti"]
    redis_conn.setex(jti, settings.AUTHJWT_ACCESS_TOKEN_EXPIRES, "true")
    return {"detail": "Tokens has been revoked"}
