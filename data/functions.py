from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from data import User
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from keyboards.all_keyboards import review_approved, review_declined, admin_suggest_to_close_appeal
from data import Appeal, Thread
import asyncio
from config import ADMINS_CHAT_ID, APPROVED_TOPIC_ID, DECLINED_TOPIC_ID, SLEEP_TIME
from keyboards.all_keyboards import get_phone_number

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

async def delete(session: AsyncSession, bot: Bot, thread: Thread, user_id: int):
    await asyncio.sleep(SLEEP_TIME)
    request = sqlalchemy.delete(Appeal).filter(Appeal.by_user == user_id, Appeal.is_review == False)
    await session.execute(request)
    request = sqlalchemy.delete(Thread).filter(Thread.by_user == user_id, Thread.is_open == False)
    await session.execute(request)
    await session.commit()
    await bot.delete_forum_topic(chat_id=ADMINS_CHAT_ID, message_thread_id=thread.message_thread_id)


async def create_topic_for_user(session: AsyncSession, bot: Bot, user_id: int):
    user = await get_user(user_id, session, bot)
    if not user:
        return
    topic = await bot.create_forum_topic(chat_id=ADMINS_CHAT_ID, name=f'❌ОТКРЫТАЯ проблема {user_id}')
    msg_text = ('Новое обращение по проблеме:'
                f'Username: {user.telegram_username}\n'
                f'Отображаемое имя: {user.telegram_name}\n'
                f'Номер телефона: {user.phone}\n\n'
                )
    await bot.send_message(chat_id=ADMINS_CHAT_ID, text=msg_text, reply_markup=admin_suggest_to_close_appeal(user_id),
                                                    message_thread_id=topic.message_thread_id)
    session.add(Thread(by_user=user_id, name=topic.name, message_thread_id=topic.message_thread_id))
    await session.commit()
    return topic


async def get_user(user_id, session, bot: Bot):
    try:
        request = sqlalchemy.select(User).filter(User.telegram_id == user_id)
        user: User = list(await session.scalars(request))[0]
        return user
    except IndexError:
        await bot.send_message(chat_id=user_id, text='Укажите Ваш номер для окончания регистрации и попробуйте ещё раз',
                             reply_markup=get_phone_number())

