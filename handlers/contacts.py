from aiogram import Router, F, types
from keyboards.all_keyboards import menu

router = Router()

@router.message(F.text == 'Контакты')
async def fetch_review(message: types.Message):
    await message.answer('Контакты поддержки: @help\n'
                         'Наш телеграмм-канал - [ссылка]\n'
                         'Наш Instagram - [ссылка]',
                         reply_markup=menu())

#TODO ALL_LINKS