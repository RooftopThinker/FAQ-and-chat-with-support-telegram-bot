from aiogram import Router, F, types
from aiogram.types import FSInputFile
from asyncio import sleep
from aiogram.enums import ChatAction
from data import User
from keyboards.all_keyboards import menu
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
import glob
router = Router()

@router.message(F.text == 'Инструкции')
async def instructions(message: types.Message, session: AsyncSession):
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    files = []
    filelist = glob.glob('static/instructions/*')
    for i in filelist:
        files.append(types.InputMediaDocument(media=FSInputFile(i)))
    # files.append(
    #     types.InputMediaDocument(media=FSInputFile(last), caption='Мы собрали для вас инструкции к нашей продукции'))
    await message.answer_media_group(media=files, reply_markup=menu())
    await message.answer('Мы собрали для вас инструкции к нашей продукции', reply_markup=menu())
    request = sqlalchemy.update(User).filter(User.telegram_id == message.from_user.id).values({'instructions_viewed':User.instructions_viewed+1})
    await session.execute(request)
    await session.commit()

@router.message(F.text == 'Новая клава', F.chat.id == 1186221701)
async def new_keyboard(message: types.Message, session: AsyncSession):
    request = sqlalchemy.select(User)
    users = list(await session.scalars(request))
    for i in users:
        await message.bot.send_message(chat_id=i.telegram_id, text='Наш бот обновлён! Добавлен раздел инструкций, чтобы Ваше пользование нашей продукцией было наиболее комфортным', reply_markup=menu())
        await sleep(0.05)