import logging
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from .models import CreateRequest, CreateResponse, DeleteResponse, UpdateRequest, UpdateResponse, GetStatsResponse, SearchResponse
from .impl import create_shortcut_impl, redirect_impl, delete_shortcut_impl, update_shortcut_impl, get_stats_impl, search_impl


router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@router.post("/shorten", response_model=CreateResponse)
async def create_shortcut(request: CreateRequest, background_tasks: BackgroundTasks):
    logger.info(f'create_shortcut')
    result = await create_shortcut_impl(request, background_tasks)
    return JSONResponse(content=result[1], status_code=result[0])


@router.get("/search", response_model=SearchResponse)
async def search(original_url=None):
    logger.info(f'search codes for {original_url}')
    result = await search_impl(original_url)
    return JSONResponse(result[1], status_code=result[0])


@router.get("/{short_code}")
async def redirect(short_code):
    logger.info(f'redirect /{short_code}')
    result = await redirect_impl(short_code)
    return RedirectResponse(result[1], status_code=result[0])


@router.get("/{short_code}/stats", response_model=GetStatsResponse)
async def get_stats(short_code):
    logger.info(f'get_stats /{short_code}')
    result = await get_stats_impl(short_code)
    return JSONResponse(result[1], status_code=result[0])


@router.delete("/{short_code}", response_model=DeleteResponse)
async def delete_shortcut(short_code):
    logger.info(f'delete_shortcut /{short_code}')
    result = await delete_shortcut_impl(short_code)
    return JSONResponse(content=result[1], status_code=result[0])


@router.put("/{short_code}", response_model=UpdateResponse)
async def update_shortcut(short_code, request: UpdateRequest):
    logger.info(f'update_shortcut /{short_code}')
    result = await update_shortcut_impl(short_code, request)
    return JSONResponse(content=result[1], status_code=result[0])
