from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.service import UrlService
from app.analytics import record_click_async
from app.models import CreateUrlRequest, UrlResponse, StatsResponse
import asyncio

router = APIRouter()


@router.post("/urls", response_model=UrlResponse, status_code=201)
async def create_url(req: CreateUrlRequest, db: AsyncSession = Depends(get_db)):
    return await UrlService(db).shorten(req)


@router.get("/{code}")
async def redirect_url(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    svc = UrlService(db)
    original = await svc.resolve(code)

    # Resolve URL record for analytics (non-blocking)
    record = await svc.repo.get_by_code(code)
    if record:
        asyncio.create_task(record_click_async(
            db,
            record.id,
            request.client.host if request.client else None,
            request.headers.get("referer"),
            request.headers.get("user-agent"),
        ))

    return RedirectResponse(url=original, status_code=302)


@router.get("/urls/{code}", response_model=UrlResponse)
async def get_url(code: str, db: AsyncSession = Depends(get_db)):
    return await UrlService(db).get_metadata(code)


@router.delete("/urls/{code}", status_code=204)
async def delete_url(code: str, db: AsyncSession = Depends(get_db)):
    await UrlService(db).deactivate(code)


@router.get("/urls/{code}/stats", response_model=StatsResponse)
async def get_stats(code: str, db: AsyncSession = Depends(get_db)):
    return await UrlService(db).get_stats(code)
