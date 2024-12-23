from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from data import User,delete_review_by_user_id
from keyboards.all_keyboards import review_approved, review_declined
router = Router()


# @router.message(F.photo, StateFilter(None))
# async def send_review(message: types.Message):
#     await message.answer("Отзыв зарегистрирован! Ожидайте прохождения модерации, или отправьте ещё отзывы для участия!")
#     await message.bot.copy_message(message_id=message.message_id, from_chat_id=message.chat.id, chat_id=ADMINS_CHAT_ID,
#                                    reply_markup=approve_or_decline_subscription(message.from_user.id))


@router.callback_query(F.data.startswith('accept'))
async def approve_review(callback: types.CallbackQuery, session: AsyncSession):
    data = int(callback.data.split('_')[1])
    # await callback.message.edit_reply_markup(reply_markup=review_approved())
    await delete_review_by_user_id(callback.from_user.id, callback.bot, session)
    request = sqlalchemy.update(User).filter(User.telegram_id == data).values(reviews_approved=User.reviews_approved+1)
    await session.execute(request)
    await session.commit()
    await callback.bot.send_message(text='Ваш отзыв принят! Мы начислили Вам бонусы для следующих покупок.', chat_id=data)


@router.callback_query(F.data.startswith('decline'))
async def decline_review(callback: types.CallbackQuery, session: AsyncSession):
    data = int(callback.data.split('_')[1])
    request = sqlalchemy.update(User).filter(User.telegram_id == data).values(reviews_declined=User.reviews_declined+1)
    await delete_review_by_user_id(callback.from_user.id, callback.bot, session, False)
    await session.execute(request)
    await session.commit()
    await callback.bot.send_message(text='К сожалению, мы не можем принять этот отзыв.', chat_id=data)
