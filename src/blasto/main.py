import logging  # to create this file's logger
import time  # to measure how long a request takes
from collections.abc import Awaitable, Callable  # types for the middleware's call_next

import uvicorn
from fastapi import (
    FastAPI,
    Request,
    Response,
)
from fastapi.responses import HTMLResponse, JSONResponse

from blasto.api.routes import applications
from blasto.config import settings
from blasto.errors import BlastoError
from blasto.logging_setup import setup_logging

setup_logging(settings.log_level)  # configure logging before anything logs
logger = logging.getLogger(
    __name__
)  # a logger named "blasto.main"; the name shows in every line


app = FastAPI()

app.include_router(applications.router)


@app.exception_handler(
    BlastoError
)  # any BlastoError (or subclass) raised in an endpoint lands here
async def blasto_error_handler(request: Request, exc: BlastoError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.code, "message": exc.message},
    )


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
      <head><title>blasto</title></head>
      <body>
        <h1>blasto</h1>
        <p>Backend for a driving school's website, in development.</p>
        <p>Version B: rollback test.</p>
        <p>Code: <a href="https://github.com/mtmsvc/blasto">github.com/mtmsvc/blasto</a></p>
      </body>
    </html>"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
