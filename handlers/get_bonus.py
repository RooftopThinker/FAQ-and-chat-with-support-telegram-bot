import sqlalchemy
from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from data import User, Appeal
from aiogram_album import AlbumMessage
from aiogram.fsm.context import FSMContext
from .fsm import GetBonus
from config import ADMINS_CHAT_ID, NEW_TOPIC_ID
from keyboards.all_keyboards import cancel, approve_or_decline_subscription, menu
import json
router = Router()


@router.message(F.text == 'Получить бонус')
async def fetch_review(message: types.Message, state: FSMContext):
    await message.answer('Спасибо за покупку и отзыв. Просьба прислать скрин инструкции, где говорится про бонус и'
                         ' скришот самого отзыва', reply_markup=cancel())
    await state.set_state(GetBonus.fetch_bank_requisite)


@router.message(F.media_group_id, GetBonus.fetch_bank_requisite)
async def fetch_requisite(message: AlbumMessage, state: FSMContext):
    media_group = []
    for m in message:
        if m.content_type != 'photo':
            await message.answer('Пожалуйста, пришлите только скриншоты. Другие медиа не принимаются.')
            return
        media_group.append({"media":m.photo[-1].file_id, "type": "photo"})
        types.InputMediaPhoto.model_dump_json()
    await message.answer('Отлично! Для оформления нам потребуется некоторые ваши данные. Пришлите нам реквизиты по которым мы можем начислить бонус\n\n'
                         '‼️ОБЯЗАТЕЛЬНО укажите банк.\n\n'
                         'В случае отсутствия банка, мы вынуждены отказать.' , reply_markup=cancel())
    await state.set_state(GetBonus.send_for_approval)
    await state.update_data(media_group=media_group)

@router.message(GetBonus.send_for_approval)
async def send_for_approval(message: AlbumMessage, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    request = sqlalchemy.select(User).filter(User.telegram_id == message.from_user.id)

    try:
        result: User = list(await session.scalars(request))[0]
    except IndexError:
        await message.answer('Вы не указали номер телефона! Напишите /start, чтобы завершить регистрацию')
        return
    media_group = await message.bot.send_media_group(media=data['media_group'], chat_id=ADMINS_CHAT_ID,
                                                         message_thread_id=NEW_TOPIC_ID)
    text = ('Отправлен новый отзыв!🔝 Данные пользователя:\n'
            f"Username: {result.telegram_username}\n"
            f"Отображаемое имя: {result.telegram_name}\n"
            f"Номер телефона: {result.phone}\n"
            f"Реквизиты: {message.text}")
    await message.answer('Отзыв отправлен! Ожидайте одобрения', reply_markup=await menu(session, message.from_user.id))

    info = await message.bot.send_message(chat_id=ADMINS_CHAT_ID,
                                       reply_markup=approve_or_decline_subscription(message.from_user.id), text=text,
                                       message_thread_id=NEW_TOPIC_ID)
    for i in media_group:
        appeal = Appeal(message_id=i.message_id, by_user=message.from_user.id, is_review=True)
        session.add(appeal)
    appeal = Appeal(message_id=info.message_id, by_user=message.from_user.id, is_review=True)
    session.add(appeal)

    await session.commit()
    await state.clear()

@router.message(GetBonus.fetch_bank_requisite,~F.media_group_id)
async def reject(message: types.Message):
    await message.answer('Мы ожидаем два скриншота')