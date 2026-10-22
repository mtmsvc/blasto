import secrets
from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyHeader

from blasto.config import settings
from blasto.errors import NotAuthorized

api_key_header = APIKeyHeader(
    name="X-API-Key", auto_error=False
)  # reads the X-API-Key header; None if missing


async def require_admin(
    api_key: Annotated[str | None, Depends(api_key_header)],
) -> None:
    expected = settings.admin_api_key
    if expected is None or api_key is None:  # no key configured, or none sent → refuse
        raise NotAuthorized()
    if not secrets.compare_digest(
        api_key.encode(), expected.get_secret_value().encode()
    ):  # constant-time comparison
        raise NotAuthorized()
