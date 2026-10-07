import logging  # to create this file's logger
import time  # to measure how long a request takes
from collections.abc import Awaitable, Callable  # types for the middleware's call_next

import uvicorn
from fastapi import (
    FastAPI,
    Request,
    Response,
)
from fastapi.responses import HTMLResponse

from blasto.config import settings
from blasto.logging_setup import setup_logging
from blasto.utils import capitalize_name

setup_logging(settings.log_level)  # configure logging before anything logs
logger = logging.getLogger(
    __name__
)  # a logger named "blasto.main"; the name shows in every line


app = FastAPI()


@app.middleware("http")  # run this function around every HTTP request
async def log_requests(
    request: Request,
    call_next: Callable[
        [Request], Awaitable[Response]
    ],  # passes the request on to the endpoint
) -> Response:
    start = time.perf_counter()  # a precise clock, made for measuring durations
    response = await call_next(request)  # let the endpoint handle the request
    duration_ms = (time.perf_counter() - start) * 1000  # elapsed time in milliseconds
    logger.info(  # an INFO line: hidden when LOG_LEVEL is WARNING or higher
        "%s %s %s %.1fms",  # placeholders, filled in by logging only if the line is shown
        request.method,  # e.g. GET
        request.url.path,  # e.g. /health
        response.status_code,  # e.g. 200
        duration_ms,  # e.g. 0.8
    )
    return response  # send the response back to the client


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return """<!doctype html>
<html>
  <head><title>BLASTO</title></head>
  <body><h1>Салам, БРАТИШШШКА!</h1></body>
</html>"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/hello/{name}")
def hello(name: str) -> dict[str, str]:
    name = capitalize_name(name)
    return {"message": f"Hello, {name}!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
