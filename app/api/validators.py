from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_crud
from app.models import CharityProject


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    proj_id = await charity_crud.get_project_id_by_name(project_name, session)
    if proj_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_before_edit(
        project_id: int,
        session: AsyncSession
) -> CharityProject:
    project = await charity_crud.get(
        obj_id=project_id, session=session
    )
    if not project:
        raise HTTPException(status_code=404, detail='Проект не найден!')
    return project


async def if_proj_closed(
        project_id: int,
        session: AsyncSession,
):
    project = await charity_crud.get(obj_id=project_id, session=session)
    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )


async def if_donations_poured(
        project_id: int,
        session: AsyncSession,
):
    project = await charity_crud.get(obj_id=project_id, session=session)
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )


async def if_new_sum_more_than_old(
        new_sum: int,
        project_id: int,
        session: AsyncSession,
):
    project = await charity_crud.get(obj_id=project_id, session=session)
    if new_sum < project.invested_amount:
        raise HTTPException(
            status_code=422,
            detail='Нельзя установить сумму меньше уже вложенной!'
        )
