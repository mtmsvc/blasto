from collections.abc import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from blasto.models import Application
from blasto.schemas.application import ApplicationCreate


async def create_application(
    session: AsyncSession, data: ApplicationCreate
) -> Application:
    application = Application(
        **data.model_dump()
    )  # the ORM object, built from the validated input
    session.add(application)
    await session.commit()  # INSERT; Postgres fills in id and created_at
    return application  # the new row, with id and created_at


async def get_application(
    session: AsyncSession, application_id: int
) -> Application | None:
    result = await session.execute(
        select(Application).where(Application.id == application_id)
    )
    return result.scalar_one_or_none()  # one or none, and anything more is an error


async def list_applications(session: AsyncSession) -> Sequence[Application]:
    result = await session.scalars(select(Application))  # wait for the database first
    return result.all()


async def update_application(
    session: AsyncSession, application_id: int, data: ApplicationCreate
) -> Application | None:
    result = await session.execute(
        update(Application)
        .where(Application.id == application_id)  # only this application
        .values(
            **data.model_dump()
        )  # every field from the form (PUT = full replacement)
        .returning(Application)  # send the updated row back
    )
    application = (
        result.scalar_one_or_none()
    )  # the updated Application, or None if no row had this ID
    await session.commit()
    return application


async def delete_application(
    session: AsyncSession, application_id: int
) -> Application | None:
    result = await session.execute(
        delete(Application)
        .where(Application.id == application_id)  # only this application
        .returning(Application)  # send the deleted row back
    )
    application = (
        result.scalar_one_or_none()
    )  # the deleted Application, or None if no row had this ID
    await session.commit()
    return application
