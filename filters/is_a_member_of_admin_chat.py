from aiogram import types, Bot
from aiogram.filters import Filter
from config import ADMINS_CHAT_ID


class IsAdmin(Filter):
    async def __call__(self, message: types.Message, bot: Bot):
        user_group_status = await bot.get_chat_member(chat_id=ADMINS_CHAT_ID, user_id=message.from_user.id)
        if user_group_status.status != 'left':
            return True
        else:
            return False