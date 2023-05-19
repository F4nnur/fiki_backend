from fastapi import APIRouter, Depends, HTTPException
from ..schemas.summary import SummarySchema, SummarySchemaCreate, SummarySchemaUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from ..services.summary import create, get_by_id, get_all, update, delete
from fastapi_jwt_auth import AuthJWT


summaries_router = APIRouter(prefix="/summaries", tags=["Summaries"])


@summaries_router.post("", response_model=SummarySchema, status_code=201)
async def create_summary(
    summary: SummarySchemaCreate,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    result = await create(db, summary)
    if not result:
        raise HTTPException(status_code=400, detail=f"User not found")
    return result


@summaries_router.patch("/{summary_id}", response_model=SummarySchema)
async def update_summary(
    summary_id: int,
    payload: SummarySchemaUpdate,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_claims = authorize.get_raw_jwt()["user_claims"]
    new_summary_data = payload.dict()
    summary = await get_by_id(db, summary_id)

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    if user_claims["id"] != summary.user_id:
        raise HTTPException(status_code=405)

    if not any(new_summary_data.values()):
        raise HTTPException(status_code=400)

    return await update(db, payload, summary)


@summaries_router.delete("/{summary_id}", status_code=204)
async def delete_summary(
    summary_id: int, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_claims = authorize.get_raw_jwt()["user_claims"]
    summary = await get_by_id(db, summary_id)

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    if user_claims["id"] != summary.user_id:
        raise HTTPException(status_code=405)

    return await delete(db, summary)


@summaries_router.get("", response_model=list[SummarySchema])
async def get_summaries(
    db: AsyncSession = Depends(get_db),
    limit: int | None = None,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    return await get_all(db, limit)


@summaries_router.get("/{summary_id}", response_model=SummarySchema)
async def get_summary(
    summary_id: int, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    summary = await get_by_id(db, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary
