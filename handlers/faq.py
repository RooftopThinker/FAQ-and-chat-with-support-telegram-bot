from aiogram import Router, F, types
from keyboards.all_keyboards import dispenser_or_humidifier, menu
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from data import User
from .fsm import FAQ
router = Router()

@router.message(F.text == 'Вопросы')
async def faq(message: types.Message, state: FSMContext):
    await message.answer('Мы подготовили ответы на часто задаваемые вопросы. Выберите категорию товара.',
                         reply_markup=dispenser_or_humidifier())
    await state.set_state(FAQ.good_chosen)


@router.message(F.data == 'dispenser', FAQ.good_chosen)
async def faq_dispenser(message: types.Message, state: FSMContext, session: AsyncSession):
    file = open('static/dispenser_faq.txt')
    text = file.read()
    request = sqlalchemy.update(User).filter(User.telegram_id == message.from_user.id).values(
        {'faq_viewed':User.faq_viewed+1}
    )
    await session.execute(request)
    for x in range(0, len(text), 4096):
        mess = text[x: x + 4096]
        await message.answer(mess, parse_mode='html', reply_markup=menu())
    await state.clear()

@router.message(F.data == 'humidifier', FAQ.good_chosen)
async def faq_dispenser(message: types.Message, state: FSMContext,  session: AsyncSession):
    file = open('static/dispenser_faq.txt')
    text = file.read()
    request = sqlalchemy.update(User).filter(User.telegram_id == message.from_user.id).values(
        {'faq_viewed': User.faq_viewed + 1}
    )
    await session.execute(request)
    for x in range(0, len(text), 4096):
        mess = text[x: x + 4096]
        await message.answer(mess, parse_mode='html', reply_markup=menu())
    await state.clear()

