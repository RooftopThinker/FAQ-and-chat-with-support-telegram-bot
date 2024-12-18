import sqlalchemy
from aiogram import Router, F, types
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from data import User
from aiogram.fsm.context import FSMContext
from .fsm import RegisterUser
from config import CHANNEL_ID, CHANNEL_INVITE_LINK
from keyboards.all_keyboards import get_phone_number, menu
from typing import Union
router = Router()


@router.message(CommandStart())
async def start_handler(message: Union[types.Message, types.CallbackQuery], state: FSMContext, session: AsyncSession):
    request = sqlalchemy.select(User).filter(User.telegram_id == message.from_user.id)
    result = list(await session.scalars(request))
    message = message if isinstance(message, types.Message) else message.message
    if not result:
        await message.answer(text='''Добро пожаловать в WiseHome! 🏡
Мы рады, что вы с нами! Вот что вы можете сделать в нашем боте:

📣 Оставить отзыв о нашем сервисе и получить бонусы.
❓ Посмотреть ответы на популярные вопросы.
🛠 Сообщить о проблеме или оставить заявку на обратную связь.

Оставьте свой номер для связи, выберите интересующий вас раздел из меню ниже, и мы с радостью поможем! 😊''', reply_markup=get_phone_number())
        await state.set_state(RegisterUser.fetch_number)
    else:
        await message.answer('''Добро пожаловать в WiseHome! 🏡
Мы рады, что вы с нами! Вот что вы можете сделать в нашем боте:

📣 Оставить отзыв о нашем сервисе и получить бонусы.
❓ Посмотреть ответы на популярные вопросы.
🛠 Сообщить о проблеме или оставить заявку на обратную связь.

Выберите интересующий вас раздел из меню ниже, и мы с радостью поможем! 😊''', reply_markup=menu())


@router.message(RegisterUser.fetch_number, F.content_type == types.ContentType.CONTACT)
async def register_user(message: types.Message, session: AsyncSession, state: FSMContext):
    username = '@' + message.from_user.username if message.from_user.username else None
    name = message.from_user.full_name
    phone = message.contact.phone_number
    id = message.from_user.id
    new_user = User(telegram_name=name, telegram_username=username, phone=phone, telegram_id=id)
    session.add(new_user)
    await session.commit()
    await message.answer('Успешная регистрация пользователя')
    await start_handler(message, state, session)


# @router.callback_query(RegisterUser.check_subscription, F.data == 'subscription')
# async def check_sub(callback: types.CallbackQuery, state: FSMContext):
#     user_channel_status = await callback.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=callback.from_user.id)
#
#     if user_channel_status.status == 'left':
#         await callback.message.answer('Не видим тебя в подписчиках канала. Попробуй ещё раз!')
#         return
#
#     await callback.message.answer('Спасибо! Видим тебя в подписчиках канала! Теперь можно принять участие в розыгрыше.',
#                                   reply_markup=types.ReplyKeyboardRemove())
#     await callback.message.delete()
#     await callback.bot.send_chat_action(callback.from_user.id, ChatAction.TYPING)
#     await sleep(5)
#
#     await callback.message.answer_photo(caption='На Wildberries: Отзывы хранятся в личном кабинете WB: «Отзывы и вопросы» - «Отзывы»\n'
#                                       'Необходимо отправить два скрина: из раздела отзыва, где будет видно товар и сам отзыв.',
#                                         photo=PHOTOS_FILES_IDS[1])
#     await callback.bot.send_chat_action(callback.from_user.id, ChatAction.TYPING)
#     await sleep(5)
#     await callback.message.answer_photo(caption='На Ozon: Отзывы хранятся в личном кабинете Ozon: «:Ждут отзыва» - «Мои отзывы»\n'
#                                         'Необходимо отправить скрин, где будет видно товар и сам отзыв.',
#                                         photo=PHOTOS_FILES_IDS[0])
#     await callback.bot.send_chat_action(callback.from_user.id, ChatAction.TYPING)
#     await sleep(5)
#     await callback.message.answer('Чтобы принять участие, отправь фото твоего отзыва, и он отправится на модерацию.'
#                                   ' После прохождения модерации мы уведомим тебя о решении.\n')
#     await state.clear()