from aiogram import Router, F, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from filters.is_a_member_of_admin_chat import IsAdmin
from data import User
import sqlalchemy
router = Router()
router.message.filter(IsAdmin())

@router.callback_query(F.data == 'stats')
async def stats(callback: types.CallbackQuery, session: AsyncSession):
    approved_sum = await session.scalar(sqlalchemy.select(sqlalchemy.func.sum(User.reviews_approved)))
    appealed_sum = await session.scalar(sqlalchemy.select(sqlalchemy.func.sum(User.problems_appealed)))
    max_id = await session.scalar(sqlalchemy.select(sqlalchemy.func.max(User.id)))
    declined_sum = await session.scalar(sqlalchemy.select(sqlalchemy.func.sum(User.reviews_declined)))
    faq_sum = await session.scalar(sqlalchemy.select(sqlalchemy.func.sum(User.faq_viewed)))
    #print(f"Approved sum: {approved_sum}, Appealed sum: {appealed_sum}, Max ID: {max_id}")
    await callback.message.answer(text=f'Отзывов принято: {approved_sum},\n'
                                       f'Отзывов отклонено: {declined_sum},\n'
                                       f'Раз вопросов просмотрено: {faq_sum},\n'
                         f'Обращений по проблемам: {appealed_sum},\n'
                         f'Пользователей: {max_id}')
