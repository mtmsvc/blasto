from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from blasto.crud import (
    application as crud,  # module alias: crud.list_applications, no name clash
)
from blasto.db import get_session
from blasto.models import Application
from blasto.schemas.application import ApplicationCreate, ApplicationPublic

router = APIRouter(prefix="/applications", tags=["applications"])

SessionDep = Annotated[
    AsyncSession, Depends(get_session)
]  # FastAPI runs get_session and passes the session in


@router.post("", status_code=201, response_model=ApplicationPublic)
async def create_application(
    session: SessionDep, new_application: ApplicationCreate
) -> Application:
    return await crud.create_application(session, new_application)


@router.get("/{application_id}", response_model=ApplicationPublic)
async def get_application(session: SessionDep, application_id: int) -> Application:
    application = await crud.get_application(session, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.get("", response_model=list[ApplicationPublic])
async def list_applications(session: SessionDep) -> Sequence[Application]:
    return await crud.list_applications(session)


@router.put("/{application_id}", response_model=ApplicationPublic)
async def update_application(
    session: SessionDep, application_id: int, updated_application: ApplicationCreate
) -> Application:
    application = await crud.update_application(
        session, application_id, updated_application
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.delete("/{application_id}", response_model=ApplicationPublic)
async def delete_application(session: SessionDep, application_id: int) -> Application:
    application = await crud.delete_application(session, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application
