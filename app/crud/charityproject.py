from typing import Optional, List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject, User
from app.schemas.charityproject import CharityProjectCreate, CharityProjectUpdate


class CRUDCharity(CRUDBase[CharityProject]):

    async def create(
            self,
            obj_in: CharityProjectCreate,
            session: AsyncSession,
            user: Optional[User] = None
    ) -> CharityProject:
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db_obj: CharityProject,
            obj_in: CharityProjectUpdate,
            session: AsyncSession,
    ) -> CharityProject:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
            self,
            db_obj: CharityProject,
            session: AsyncSession,
    ) -> CharityProject:
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_proj_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        db_proj_id = db_proj_id.scalars().first()
        return db_proj_id

    async def get(
            self,
            obj_id: int,
            session: AsyncSession
    ) -> Optional[CharityProject]:
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ) -> List[CharityProject]:
        projs = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested
            ).order_by(
                CharityProject.close_date -
                CharityProject.create_date
            )
        )
        projs = projs.scalars().all()
        return projs


charity_crud = CRUDCharity(CharityProject)
