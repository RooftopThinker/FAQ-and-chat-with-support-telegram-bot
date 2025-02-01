import sqlalchemy
import os
import pandas as pd
from datetime import datetime
from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from data import User
from filters import IsAdmin
from config import DELETE_EXPORTS
router = Router()
router.message.filter(IsAdmin())

def to_dict(row):
    if row is None:
        return None

    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict



async def exportexcel(session: AsyncSession):
    request = sqlalchemy.select(User)
    data = list(await session.scalars(request))
    data_list = [to_dict(item) for item in data]
    df = pd.DataFrame(data_list)
    now = datetime.now().strftime("%Y_%d_%m_%H_%M_%S")
    filename = f'exports\\{now}.xlsx'
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer, sheet_name='users')
    writer.close()
    return filename


@router.callback_query(F.data == 'export')
async def send_review(callback: types.CallbackQuery, session: AsyncSession):
    await callback.message.answer("Формирую таблицу Excel...")
    filename = await exportexcel(session)
    await callback.message.answer_document(document=types.FSInputFile(filename))
    if DELETE_EXPORTS:
        os.remove(filename)
