from fastapi import APIRouter, Depends, HTTPException
from ..schemas.comment import CommentSchema, CommentSchemaCreate, CommentSchemaUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from ..services.comment import create, update, delete, get_by_id, get_all
from fastapi_jwt_auth import AuthJWT


comments_router = APIRouter(prefix="/comments", tags=["Comments"])


@comments_router.get("", response_model=list[CommentSchema])
async def get_comments(
    db: AsyncSession = Depends(get_db),
    limit: int | None = None,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    return await get_all(db, limit)


@comments_router.get("/{comment_id}", response_model=CommentSchema)
async def get_comment(
    comment_id: int, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    comment = await get_by_id(db, comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@comments_router.post("", response_model=CommentSchema, status_code=201)
async def create_comment(
    comment: CommentSchemaCreate, db: AsyncSession = Depends(get_db)
):
    result = await create(db, comment)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=f"{result} not found")
    return result


@comments_router.patch("/{comment_id}", response_model=CommentSchema)
async def update_comment(
    comment_id: int,
    payload: CommentSchemaUpdate,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_claims = authorize.get_raw_jwt()["user_claims"]
    new_comment_data = payload.dict()
    comment = await get_by_id(db, comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if user_claims["id"] != comment.user_id:
        raise HTTPException(status_code=405)

    if not any(new_comment_data.values()):
        raise HTTPException(status_code=400)

    return await update(db, payload, comment)


@comments_router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_claims = authorize.get_raw_jwt()["user_claims"]
    comment = await get_by_id(db, comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if user_claims["id"] != comment.user_id:
        raise HTTPException(status_code=405)

    return await delete(db, comment)
