from aiohttp import ClientSession, web
from dotenv import load_dotenv
import asyncio
import logging
import os


TIMEOUT = 3


logger = logging.getLogger(__name__)


load_dotenv()
api_key = os.getenv('OPENWEATHER_API_KEY')


async def get_current_temperature(city: str):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={api_key}&units=metric'
    async with ClientSession() as session:
        try:
            async with session.get(url, timeout=TIMEOUT) as response:
                x = await response.json()
                if x['cod'] != 200:
                    logger.error(f'openweathermap api call failed with "{city}": {x}')
                    return None
                logger.info(f'openweathermap api call results for "{city}": {x["main"]}')
                return x['main']['temp']
        except asyncio.TimeoutError:
            logger.info(f'openweathermap api call for "{city}" took too long, aborting')
            return None
