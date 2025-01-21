from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.all_keyboards import menu

router = Router()

@router.message(F.text == 'Контакты')
async def fetch_review(message: types.Message, session: AsyncSession):
    await message.answer('Контакты поддержки: @help\n'
                         'Наш телеграмм-канал - [ссылка]\n'
                         'Наш Instagram - [ссылка]',
                         reply_markup=await menu(session, message.from_user.id))

#TODO ALL_LINKS