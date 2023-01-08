from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_name_duplicate, check_project_before_edit,
    if_new_sum_more_than_old, if_donations_poured, if_proj_closed
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_crud
from app.models import Donation
from app.schemas.charityproject import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.investment import process_investment_charity

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(session: AsyncSession = Depends(get_async_session)):
    projects = await charity_crud.get_multi(session)
    return projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_project(
        project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    await check_name_duplicate(project.name, session)
    new_proj = await charity_crud.create(project, session)
    await process_investment_charity(new_proj, Donation, session)
    return new_proj


@router.patch('/{proj_id}', response_model=CharityProjectDB, dependencies=[Depends(current_superuser)],)
async def update_project(
        proj_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    await if_proj_closed(proj_id, session)
    if obj_in.full_amount:
        await if_new_sum_more_than_old(obj_in.full_amount, proj_id, session)
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    project = await check_project_before_edit(
        proj_id, session
    )
    project = await charity_crud.update(
        db_obj=project,
        obj_in=obj_in,
        session=session,
    )
    await process_investment_charity(project, Donation, session)
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def remove_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    project = await check_project_before_edit(
        project_id, session
    )
    await if_donations_poured(project_id, session)
    meeting_room = await charity_crud.remove(project, session)
    return meeting_room
