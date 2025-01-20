from aiogram import Router, F, types, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from keyboards.all_keyboards import yes_or_no, problem_solved, menu
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
    await message.bot.send_message(text='Ответ на Ваше обращение🔝. Ваша проблема решена?', chat_id=appeal.by_user,
                                   reply_markup=yes_or_no())
    user_state: FSMContext = FSMContext(storage=dispatcher.storage, key=StorageKey(
        chat_id=appeal.by_user, user_id=appeal.by_user, bot_id=message.bot.id))
    await user_state.set_state(IsProblemSolved.question)
    await message.reply('Ответ на обращение доставлен пользователю')


@router.message(IsProblemSolved.question)
async def is_problem_solved(message: types.Message):
    await message.answer('Выберите, решена ли Ваша проблема')


@router.callback_query(IsProblemSolved.question, F.data.in_({'yes', 'no'}))
async def is_problem_solved(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == 'yes':
        await schedule_deletion_by_user_id(callback.from_user.id, callback.bot, session)
        await callback.message.edit_reply_markup()
        await callback.message.answer('Рады были помочь! Спасибо, что выбрали WiseHome', reply_markup=menu())
        await state.clear()
    else:
        await callback.message.answer('Напишите ответное сообщение службе поддержки', reply_markup=problem_solved())
        await state.set_state(Problems.problem_reported)


@router.callback_query(F.data == 'problemsolved')
async def problemsolved(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await schedule_deletion_by_user_id(callback.from_user.id, callback.bot, session)
    await callback.message.edit_reply_markup()
    await callback.message.answer('Рады были помочь! Спасибо, что выбрали WiseHome', reply_markup=menu())
    await state.clear()


