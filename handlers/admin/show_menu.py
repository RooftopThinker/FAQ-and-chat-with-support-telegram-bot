from aiogram import Router, F, types
from aiogram.filters import Command
from filters.is_a_member_of_admin_chat import IsAdmin
from keyboards.all_keyboards import admin_menu
from typing import Union
router = Router()

@router.message(Command('admin'), IsAdmin())
async def show_menu(update: Union[types.Message, types.CallbackQuery]):
    update = update if isinstance(update, types.Message) else update.message
    await update.answer(text='Выберите действие:', reply_markup=admin_menu())
