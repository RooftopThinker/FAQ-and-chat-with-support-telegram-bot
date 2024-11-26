import sqlalchemy
from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
from data import User
from aiogram_album import AlbumMessage
from aiogram.fsm.context import FSMContext
from .fsm import GetBonus
from config import ADMINS_CHAT_ID
from keyboards.all_keyboards import cancel, approve_or_decline_subscription
router = Router()


@router.message(F.text == 'Получить бонус')
async def fetch_review(message: types.Message, state: FSMContext):
    await message.answer('Спасибо за покупку и отзыв. Просьба прислать скрин инструкции, где говорится про бонус и'
                         ' скришот самого отзыва', reply_markup=cancel())
    await state.set_state(GetBonus.fetch_bank_requisite())


@router.message(F.photo, GetBonus.fetch_bank_requisite)
async def fetch_requisite(message: AlbumMessage, state: FSMContext):
    media_group = []
    for m in message:
        if m.content_type != 'photo':
            await message.answer('Пожалуйста, пришлите только скриншоты. Другие медиа не принимаются.')
            return
        media_group.append(types.InputMediaPhoto(media=m.photo[-1].file_id))
    await message.answer('Отлично! Для оформления нам потребуется некоторые ваши данные.'
                         ' Пришлите нам реквизиты по которым мы можем начислить бонус,'
                         ' обязательно укажите банк.', reply_markup=cancel())
    await state.set_state(GetBonus.send_for_approval())
    await state.update_data(media_group=media_group)

@router.message(GetBonus.send_for_approval)
async def send_for_approval(message: AlbumMessage, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await message.bot.send_media_group(media=data['media_group'], chat_id=ADMINS_CHAT_ID)
    request = sqlalchemy.select(User).filter(User.telegram_id == message.from_user.id)
    result: User = list(await session.scalars(request))[0]
    text = ('Отправлен новый отзыв!🔝 Данные пользователя:'
            f"Username: {result.telegram_username}"
            f"Отображаемое имя: {result.telegram_name},"
            f"Номер телефона: {result.phone}")

    await message.bot.send_message(chat_id=ADMINS_CHAT_ID, reply_markup=approve_or_decline_subscription(message.from_user.id), text=text)
