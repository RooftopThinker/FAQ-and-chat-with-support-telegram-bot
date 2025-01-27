from typing import Callable, Awaitable, Dict, Any, Union

from sqlalchemy.util import await_only

from handlers.fsm import RegisterUser
import sqlalchemy
from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext
from keyboards.all_keyboards import get_phone_number
from data import User
from sqlalchemy.ext.asyncio import AsyncSession

class RegistrationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        state: FSMContext = data.get("state")
        message = event
        if message.text == '/start' or await state.get_state() in RegisterUser:
            return await handler(message, data)
        request = sqlalchemy.select(User).filter(User.telegram_id == message.from_user.id)
        result = list(await session.scalars(request))
        if not result:
            await message.answer(text='Укажите Ваш номер для окончания регистрации и попробуйте ещё раз',
                               reply_markup=get_phone_number())
            await state.set_state(RegisterUser.fetch_number)
            return
        data['user'] = result[0]
        return await handler(message, data)