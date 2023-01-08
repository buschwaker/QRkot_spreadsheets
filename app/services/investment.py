from datetime import datetime
from typing import Type

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import CharityBase


async def calculation(obj_created: CharityBase, obj_in_db: CharityBase):
    money_left_proj = obj_created.full_amount - obj_created.invested_amount
    money_left_donat = obj_in_db.full_amount - obj_in_db.invested_amount
    if money_left_proj > money_left_donat:
        obj_created.invested_amount += money_left_donat
        obj_in_db.invested_amount = obj_in_db.full_amount
        obj_in_db.fully_invested = True
        obj_in_db.close_date = datetime.now()
    elif money_left_proj == money_left_donat:
        obj_created.invested_amount = obj_created.full_amount
        obj_in_db.invested_amount = obj_in_db.full_amount
        obj_in_db.fully_invested = True
        obj_created.fully_invested = True
        obj_in_db.close_date = datetime.now()
        obj_created.close_date = datetime.now()
    else:  # money_left_proj < money_left_donat
        obj_in_db.invested_amount += money_left_proj
        obj_created.invested_amount = obj_created.full_amount
        obj_created.fully_invested = True
        obj_created.close_date = datetime.now()
    return obj_created, obj_in_db


async def process_investment_charity(
        obj_created: CharityBase,
        model_objs_in_db: Type[CharityBase],
        session: AsyncSession):
    donations_left = await session.execute(
        select(model_objs_in_db).where(
            model_objs_in_db.fully_invested == 0).order_by(
            asc(model_objs_in_db.create_date)
        )
    )
    donations_left = donations_left.scalars().all()
    for donation in donations_left:
        charity, donation = await calculation(obj_created, donation)
        session.add(charity)
        session.add(donation)
    await session.commit()
    await session.refresh(obj_created)
    return obj_created
