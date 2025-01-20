from aiogram import Router, types, F
from aiogram.enums import ChatType
from keyboards.all_keyboards import menu, send_appeal
router = Router()
router.message.filter(F.chat.type == ChatType.PRIVATE)
@router.message()
async def unendified_message(message: types.Message):
    await message.answer('Я не могу разобрать сообщение. Вы можете воспользоваться меню для работы со мной, или, '
                         'если у Вас возникла проблема, я могу связать Вас со службой поддержки.',
                         reply_markup=send_appeal())


@router.callback_query(F.data == 'send_appeal')
async def send_appeal(message: types.Message):
    pass
