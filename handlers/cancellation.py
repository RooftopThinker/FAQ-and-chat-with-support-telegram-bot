from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from .start import start_handler
from .admin.show_menu import show_menu
from sqlalchemy.ext.asyncio import AsyncSession
router = Router()

@router.callback_query(F.data == 'cancel')
async def fetch_review(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.clear()
    await callback.message.delete()
    await start_handler(callback, state, session)


@router.callback_query(F.data == 'admin_cancel')
async def fetch_review(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await show_menu(callback)