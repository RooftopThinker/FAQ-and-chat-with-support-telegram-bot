from aiogram import Router, F, types
router = Router()

@router.message(F.text == 'Контакты')
async def fetch_review(message: types.Message):
    await message.answer('Контакты поддержки: @help\n'
                         'Наш телеграмм-канал - [ссылка]\n'
                         'Наш Instagram - [ссылка]')

#TODO ALL_LINKS