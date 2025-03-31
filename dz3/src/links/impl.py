import asyncio
import random
import string
import logging
import datetime
from uuid import uuid1
from .models import CreateRequest, CreateResponse, DeleteResponse, UpdateRequest, UpdateResponse
from fastapi import HTTPException, BackgroundTasks
from dataclasses import dataclass, asdict


@dataclass
class Link:
    url: str
    creation_time: datetime.date
    access_time: datetime.date
    access_count: int


data_lock = asyncio.Lock()
data = {}
url_to_short_code = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def get_link(short_code) -> str:
    async with data_lock:
        if short_code in data:
            data[short_code].access_time = str(datetime.datetime.now())
            data[short_code].access_count += 1
            return data[short_code].url
        return None


async def save_link(short_code, url) -> bool:
    async with data_lock:
        if short_code in data:
            return False
        data[short_code] = Link(url, str(datetime.datetime.now()), 'not accessed', 0)
        if url not in url_to_short_code:
            url_to_short_code[url] = set()
        url_to_short_code[url].add(short_code)
        return True


async def update_link(short_code, url) -> bool:
    async with data_lock:
        if short_code not in data:
            return False
        url_to_short_code[data[short_code].url].remove(short_code)
        data[short_code].url = url
        if url not in url_to_short_code:
            url_to_short_code[url] = set()
        url_to_short_code[url].add(short_code)
        return True


async def delete_link(short_code) -> bool:
    async with data_lock:
        if short_code not in data:
            return False
        url_to_short_code[data[short_code].url].remove(short_code)
        del data[short_code]
        return True


async def get_stats(short_code):
    async with data_lock:
        if short_code not in data:
            return False
        return asdict(data[short_code])


async def generate_short_code() -> str:
    while True:
        characters = string.ascii_letters + string.digits
        short_code = ''.join(random.choice(characters) for i in range(8))
        async with data_lock:
            if short_code not in data:
                return short_code


def is_valid(short_code) -> bool:
    if short_code == 'search':
        return False
    return True


async def create_shortcut_impl(request: CreateRequest, background_tasks: BackgroundTasks):
    short_code = request.alias
    if not short_code:
        short_code = await generate_short_code()
    logger.info(f'short code is {short_code}')
    if not is_valid(short_code) or not await save_link(short_code, request.url):
        raise HTTPException(status_code=404, detail=f'alias \'{short_code}\' is not available')
    if request.expires_at is not None:
        background_tasks.add_task(cleanup_link, short_code,  request.expires_at)
    return 200, {'short_code': short_code}


async def redirect_impl(short_code):
    url = await get_link(short_code)
    if url is None:
        raise HTTPException(status_code=404, detail=f'short code \'{short_code}\' does not refer to any url')
    logger.info(f'{short_code} redirect to {url}')
    return 307, url


async def delete_shortcut_impl(short_code):
    result = await delete_link(short_code)
    if not result:
        raise HTTPException(status_code=404, detail=f'short code \'{short_code}\' does not refer to any url')
    return 200, 'OK'


async def update_shortcut_impl(short_code, request: UpdateRequest):
    result = await update_link(short_code, request.url)
    if not result:
        raise HTTPException(status_code=404, detail=f'short code \'{short_code}\' does not refer to any url')
    return 200, 'OK'


async def get_stats_impl(short_code):
    result = await get_stats(short_code)
    if not result:
        raise HTTPException(status_code=404, detail=f'short code \'{short_code}\' does not refer to any url')
    return 200, result


async def search_impl(url):
    if url is None:
        raise HTTPException(status_code=404, detail=f'pass url to search for')
    async with data_lock:
        result = []
        if url in url_to_short_code:
            result = list(url_to_short_code[url])
    return 200, result


async def cleanup_link(short_code, expires_at):
    t = 0
    now = datetime.datetime.now()
    if now < expires_at:
        t = (expires_at - now).total_seconds()
    await asyncio.sleep(t)
    logger.info(f'deleting expired link \'{short_code}\'')
    return await delete_shortcut_impl(short_code)
