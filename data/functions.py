from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from keyboards.all_keyboards import review_approved, review_declined
from data import Appeal, Thread
import asyncio
from config import ADMINS_CHAT_ID, APPROVED_TOPIC_ID, DECLINED_TOPIC_ID, SLEEP_TIME
from handlers.fsm import IsProblemSolved, Problems

# async def delete_appeal_by_user_id(id, bot, session):
#     request = sqlalchemy.select(Appeal).filter(Appeal.by_user == id, Appeal.is_review == False)
#     result: List[Appeal] = list(await session.scalars(request))
#     for i in result:
#         try:
#             await bot.forward_message(chat_id=ADMINS_CHAT_ID, from_chat_id=ADMINS_CHAT_ID,
#                                                message_thread_id=ANSWERED_APPEALS_TOPIC_ID, message_id=i.message_id)
#             await bot.delete_message(chat_id=ADMINS_CHAT_ID, message_id=i.message_id)
#             await sleep(0.1)
#         except (TelegramBadRequest, TelegramForbiddenError):
#             pass
#     request = sqlalchemy.delete(Appeal).filter(Appeal.by_user == id, Appeal.is_review == False)
#     await session.execute(request)
#     await session.commit()



async def delete_review_by_user_id(id, bot: Bot, session, approve=True):
    topic = APPROVED_TOPIC_ID if approve else DECLINED_TOPIC_ID
    request = sqlalchemy.select(Appeal).filter(Appeal.by_user == id, Appeal.is_review == True)
    result: List[Appeal] = list(await session.scalars(request))
    for i in result:
        try:
            await bot.forward_message(chat_id=ADMINS_CHAT_ID, from_chat_id=ADMINS_CHAT_ID,
                                               message_thread_id=topic, message_id=i.message_id)
            await asyncio.sleep(0.1)
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
        try:
            await bot.delete_message(chat_id=ADMINS_CHAT_ID, message_id=i.message_id)
        except (TelegramBadRequest, TelegramForbiddenError):
            keyboard = review_approved() if approve else review_declined()
            try:
                await bot.edit_message_reply_markup(chat_id=ADMINS_CHAT_ID, message_id=i.message_id, reply_markup=keyboard)
            except (TelegramBadRequest, TelegramForbiddenError):
                pass
    request = sqlalchemy.delete(Appeal).filter(Appeal.by_user == id, Appeal.is_review == True)
    await session.execute(request)
    await session.commit()


async def schedule_deletion_by_user_id(id, bot: Bot, session):
    # request = sqlalchemy.select(Appeal).filter(Appeal.by_user == id, Appeal.is_review == False)
    request = sqlalchemy.select(Thread).filter(Thread.by_user == id, Thread.is_open == True)
    result: Thread = list(await session.scalars(request))[0]
    await bot.send_message(chat_id=ADMINS_CHAT_ID, message_thread_id=result.message_thread_id,
                           text='✅Пользователь закрыл обращение')
    await bot.edit_forum_topic(chat_id=ADMINS_CHAT_ID, message_thread_id=result.message_thread_id,
                               name=result.name.replace("❌ОТКРЫТАЯ","(✅Закрыто)"))
    request = sqlalchemy.update(Thread).filter(Thread.by_user == id).values(is_open=False)
    await session.execute(request)
    await session.commit()
    task = asyncio.create_task(delete(session, bot, result, id))


async def delete(session: AsyncSession, bot: Bot, thread: Thread, id: int):
    await asyncio.sleep(SLEEP_TIME)
    request = sqlalchemy.delete(Appeal).filter(Appeal.by_user == id, Appeal.is_review == False)
    await session.execute(request)
    request = sqlalchemy.delete(Thread).filter(Thread.by_user == id, Thread.is_open == False)
    await session.execute(request)
    await session.commit()
    await bot.delete_forum_topic(chat_id=ADMINS_CHAT_ID, message_thread_id=thread.message_thread_id)