from aiogram import Router, F, types, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy

from handlers.admin.export_to_excel import to_dict
from keyboards.all_keyboards import yes_or_no, problem_solved, menu
from data import Appeal
from asyncio import sleep
from config import ADMINS_CHAT_ID, ANSWERED_APPEALS_TOPIC_ID, APPROVED_TOPIC_ID, DECLINED_TOPIC_ID
from handlers.fsm import IsProblemSolved, Problems

async def delete_appeal_by_user_id(id, bot, session):
    request = sqlalchemy.select(Appeal).filter(Appeal.by_user == id, Appeal.is_review == False)
    result: List[Appeal] = list(await session.scalars(request))
    for i in result:
        try:
            await bot.forward_message(chat_id=ADMINS_CHAT_ID, from_chat_id=ADMINS_CHAT_ID,
                                               message_thread_id=ANSWERED_APPEALS_TOPIC_ID, message_id=i.message_id)
            await bot.delete_message(chat_id=ADMINS_CHAT_ID, message_id=i.message_id)
            await sleep(0.1)
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
    request = sqlalchemy.delete(Appeal).filter(Appeal.by_user == id, Appeal.is_review == False)
    await session.execute(request)
    await session.commit()


async def delete_review_by_user_id(id, bot, session, approve=True):
    topic = APPROVED_TOPIC_ID if approve else DECLINED_TOPIC_ID
    request = sqlalchemy.select(Appeal).filter(Appeal.by_user == id, Appeal.is_review == True)
    result: List[Appeal] = list(await session.scalars(request))
    for i in result:
        try:
            await bot.forward_message(chat_id=ADMINS_CHAT_ID, from_chat_id=ADMINS_CHAT_ID,
                                               message_thread_id=topic, message_id=i.message_id)
            await sleep(0.1)
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
        try:
            await bot.delete_message(chat_id=ADMINS_CHAT_ID, message_id=i.message_id)
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
    request = sqlalchemy.delete(Appeal).filter(Appeal.by_user == id, Appeal.is_review == True)
    await session.execute(request)
    await session.commit()