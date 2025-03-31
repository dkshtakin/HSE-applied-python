import httpx
import pytest
from src.links.impl import generate_short_code, is_valid


pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_short_code_gen():
    codes = set()
    n = 100
    for i in range(n):
        code = await generate_short_code()
        codes.add(code)
    assert len(codes) == n


@pytest.mark.asyncio
async def test_validation():
    assert is_valid('hello')
    assert is_valid(await generate_short_code())
    assert is_valid('search_me')
    assert not is_valid('search')
