from aiogram import Router, F, types, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from keyboards.all_keyboards import return_to_menu, problem_solved, menu, yes_or_no
from data import Appeal
from asyncio import sleep
from config import ADMINS_CHAT_ID
from ..fsm import IsProblemSolved, Problems
from data import schedule_deletion_by_user_id
router = Router()
# router.message.filter(IsAdmin())

@router.message(F.chat.id == int(ADMINS_CHAT_ID), F.reply_to_message)
async def answer_to_appeal(message: types.Message, session: AsyncSession, dispatcher: Dispatcher):
    request = sqlalchemy.select(Appeal).filter(Appeal.message_id == message.reply_to_message.message_id)
    try:
        appeal = list(await session.scalars(request))[0]
    except IndexError:
        return
    try:
        await message.bot.copy_message(message_id=message.message_id, from_chat_id=ADMINS_CHAT_ID,
                                   chat_id=appeal.by_user)
    except (TelegramBadRequest,TelegramForbiddenError):
        await message.reply(text="Сообщение не было доставлено. Скорее всего пользователь заблокировал бота")
        return
    await message.reply('Ответ на обращение доставлен пользователю')
    if not appeal.is_review:
        await message.bot.send_message(text='Ответ на Ваше обращение🔝. Чат находится в режиме общения с поддержкой.\n\nЕсли это решило Вашу проблему,'
                                            ' закройте обращение кнопкой снизу.', chat_id=appeal.by_user, reply_markup=return_to_menu())
        user_state: FSMContext = FSMContext(storage=dispatcher.storage, key=StorageKey(
            chat_id=appeal.by_user, user_id=appeal.by_user, bot_id=message.bot.id))
        await user_state.set_state(Problems.problem_reported)


@router.message(F.text == 'Закрыть проблему')
@router.message(IsProblemSolved.question)
async def is_problem_solved(message: types.Message, state: FSMContext):
    await message.answer('Выберите, решена ли Ваша проблема', reply_markup=yes_or_no())
    await state.set_state(IsProblemSolved.question)

@router.callback_query(F.data.startswith('suggest_'))
async def admin_suggested_to_close_appeal(callback: types.CallbackQuery, dispatcher: Dispatcher):
    user_id = int(callback.data.split('_')[1])
    await callback.message.reply("Пользователю было отправлено предложение закрыть проблему")
    await callback.bot.send_message(chat_id=user_id, text='Служба поддержки предлагает Вам закрыть обращение.\n'
                                                          'Ваша проблема решена?', reply_markup=yes_or_no())
    user_state: FSMContext = FSMContext(storage=dispatcher.storage, key=StorageKey(
        chat_id=user_id, user_id=user_id, bot_id=callback.bot.id))
    await user_state.set_state(IsProblemSolved.question)


@router.callback_query(IsProblemSolved.question, F.data.in_({'yes', 'no'}))
async def is_problem_solved(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == 'yes':
        await schedule_deletion_by_user_id(callback.from_user.id, callback.bot, session)
        await callback.message.edit_reply_markup()
        await callback.message.answer('Рады были помочь! Спасибо, что выбрали WiseHome', reply_markup=await menu(session, callback.from_user.id))
        await state.clear()
    else:
        await callback.message.answer('Чат возвращён в состояние общения со службой поддержки', reply_markup=problem_solved())
        await state.set_state(Problems.problem_reported)


@router.callback_query(F.data == 'problemsolved')
async def problemsolved(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await schedule_deletion_by_user_id(callback.from_user.id, callback.bot, session)
    await callback.message.edit_reply_markup()
    await callback.message.answer('Рады были помочь! Спасибо, что выбрали WiseHome', reply_markup=await menu(session, callback.from_user.id))
    await state.clear()


