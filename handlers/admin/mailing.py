import sqlalchemy
from aiogram import Router, F, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from data import User
from filters.is_a_member_of_admin_chat import IsAdmin
from keyboards.all_keyboards import cancel, yes_or_no
from aiogram.fsm.context import FSMContext
from ..fsm import SendMailing
from typing import List
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from asyncio import sleep
router = Router()

@router.message(Command('admin'), IsAdmin())
async def show_menu(message: types.Message, state: FSMContext):
    await message.answer(text='Пришлите сообщение, которое необходимо отправить пользователям',
                         reply_markup=cancel())
    await state.set_state(SendMailing.approve)


@router.message(SendMailing.approve, IsAdmin(), ~F.media_group_id)
async def approve(message: types.Message, state: FSMContext):
    await state.update_data(message=message)
    await message.answer('Отправить рассылку?', reply_markup=yes_or_no())
    await state.set_state(SendMailing.send_mailing)


@router.callback_query(SendMailing.send_mailing, F.data == 'yes')
async def send_mailing(message: types.Message, state: FSMContext, session: AsyncSession):
    await message.answer('Рассылка запущена..')
    request = sqlalchemy.select(User)
    result: List[User] = list(await session.scalars(request))
    data = await state.get_data()
    bot_blocked_info = ''
    bot_blocked_counter = 0
    await state.clear()
    for user in result:
        try:
            await data['message'].copy_to(user.telegram_id)
            await sleep(0.05)
        except TelegramForbiddenError:
            bot_blocked_counter+=1
            bot_blocked_info+=f"Username: {user.telegram_username}\n"
            f"Отображаемое имя: {user.telegram_name}\n"
            f"Номер телефона: {user.phone}\n\n"

    if bot_blocked_counter:
        try:
            await message.answer(f'Рассылка завершена.'
                                f' Сообщение не было доставлено пользователям, заблокировавшим бота:\n {bot_blocked_info}')
        except TelegramBadRequest:
            await message.answer(f"Рассылка завершена. "
                                 f"Сообщение не было доставлено пользователям, заблокировавшим бота{bot_blocked_counter}")