from aiohttp import ClientSession, web
from dotenv import load_dotenv
import asyncio
import logging
import os
import openfoodfacts


TIMEOUT = 3
api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")

logger = logging.getLogger(__name__)


load_dotenv()

async def get_food_info(food: str):
    x = api.product.text_search(food)
    products = x.get('products', [])
    if products:
        first_product = products[0]
        result = {
            'name': first_product.get('product_name', None),
            'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
        }
        logger.info(f'openweathermap api call results for "{food}": {result}')
        return result
    logger.info(f'openweathermap api call has no information about "{food}"')
    return None
