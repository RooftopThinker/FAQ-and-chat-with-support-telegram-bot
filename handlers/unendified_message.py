from aiogram import Router, types
from keyboards.all_keyboards import menu
router = Router()

@router.message()
async def unendified_message(message: types.Message):
    await message.answer('Я не могу разобрать сообщение. Вы можете воспользоваться меню для работы со мной',
                         reply_markup=menu())

