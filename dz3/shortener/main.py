import logging
import uvicorn
from fastapi import FastAPI
from links.router import router


logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:\t[%(asctime)s]: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


app = FastAPI(
    title="url_shortener",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)
app.include_router(router, prefix="/links")


@app.get('/')
async def root():
    return {'status': 'App healthy'}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
