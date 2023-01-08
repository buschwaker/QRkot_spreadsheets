from typing import List

from aiogoogle import Aiogoogle
from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charityproject import charity_crud
from app.schemas.charityproject import CharityProjectDB
from app.services.google_api import (set_user_permissions, spreadsheets_create,
                          spreadsheets_update_value)
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    '/',
    response_model=List[CharityProjectDB],
    dependencies=[Depends(current_superuser)],
)
async def get_google_sheet(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    projects = await charity_crud.get_projects_by_completion_rate(
        session
    )
    spreadsheet_id = await spreadsheets_create(wrapper_services)
    await set_user_permissions(spreadsheet_id, wrapper_services)
    await spreadsheets_update_value(spreadsheet_id, projects, wrapper_services)
    return projects