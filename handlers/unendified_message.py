import sqlalchemy
from aiogram import Router, types, F
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from data import Thread
from handlers.fsm import BackToTalk, Problems
from keyboards.all_keyboards import menu, send_appeal, yes_or_no, return_to_menu

router = Router()
router.message.filter(F.chat.type == ChatType.PRIVATE)
@router.message()
async def unendified_message(message: types.Message, session: AsyncSession, state: FSMContext):
    request = sqlalchemy.select(Thread).filter(Thread.by_user == message.from_user.id,
                                               Thread.is_open == True)
    opened_thread = list(await session.scalars(request))
    if not opened_thread:
        await message.answer('Я не могу разобрать сообщение. Вы можете воспользоваться меню для работы со мной, или, '
                             'если у Вас возникла проблема, я могу связать Вас со службой поддержки.',
                             reply_markup=send_appeal())
    else:
        await message.answer('Я не могу разобрать сообщение. Вернуть Вас в режим общения со службой поддержки?',
                             reply_markup=yes_or_no())
        await state.set_state(BackToTalk.confirm)


@router.callback_query(F.data == 'yes', BackToTalk.confirm)
async def unendified_message(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer('Вы возвращены в режим общения с поддержкой', reply_markup=return_to_menu())
    await state.set_state(Problems.problem_reported)




# @router.callback_query(F.data == 'send_appeal')
# async def send_appeal(message: types.Message):

